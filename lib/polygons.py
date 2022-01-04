import re


def centroid(bbox):
    """
    `bbox` is a dict composed of at least four keys:
    x, y, h and w
    Return the coordinates of the centroid of the rectangle defined by `bbox`
    """
    return (bbox['x']+bbox['w']/2, bbox['y']+bbox['h']/2)


def segment(p, q, r):
    """
    `p`, `q`, `r` are three colinear points.
    Return True if q is on segment pr
    """
    return ((q[0] <= max(p[0], r[0])) &
        (q[0] >= min(p[0], r[0])) &
        (q[1] <= max(p[1], r[1])) &
        (q[1] >= min(p[1], r[1])))


def orientation(p, q, r):
    """
    `p`, `q` and `r` are three points.
    Return 0 is they are colinear, 1 if their orientation is clockwise,
    2 if it is counterclockwise
    """
    val = (((q[1] - p[1]) *
            (r[0] - q[0])) -
           ((q[0] - p[0]) *
            (r[1] - q[1])))

    if val == 0:
        return 0
    if val > 0:
        return 1
    else:
        return 2


def intersect(p1, q1, p2, q2):
    """
    Return True if `p1-p2` intersects with `q1-q2`
    """
    # Find the four orientations needed for
    # general and special cases 
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases 
    # p1, q1 and p2 are collinear and 
    # p2 lies on segment p1q1 
    if (o1 == 0) and (segment(p1, p2, q1)):
        return True

    # p1, q1 and p2 are collinear and 
    # q2 lies on segment p1q1 
    if (o2 == 0) and (segment(p1, q2, q1)):
        return True

    # p2, q2 and p1 are collinear and 
    # p1 lies on segment p2q2 
    if (o3 == 0) and (segment(p2, p1, q2)):
        return True

    # p2, q2 and q1 are collinear and 
    # q1 lies on segment p2q2 
    if (o4 == 0) and (segment(p2, q1, q2)):
        return True

    return False


def inter_list(a, b):
    """
    `a` and `b` are two lists of int or str that can be turn into int
    Return a kind-of intersection of the two lists; items are converted to str.
    Example:
    - [ 3 5   7   9 ]
    and
    -     [ 6   8   10 12 ]
    will be [ 6 7 9 ]
    """
    a = sorted([int(x) for x in a])
    b = sorted([int(x) for x in b])
    lower_bound = max(a[0], b[0])
    upper_bound = min(a[-1], b[-1])
    inter = [x for x in a+b if x <= upper_bound and x >= lower_bound]
    return sorted(map(lambda x: str(x), inter), key=int)


class DNA:
    """
    Class defining a Do-Not-Annotate region. It is defined by a list of activity types to filter.
    `video_files`: list of video files to consider. If empty, all files are considered.
    `frames`: duet of integers (starting and ending frames)
    `activity_types`: list of activities to consider. If empty, all types are considered.
    `points`: tuple of duets of integers, describing a polygon (each duet represents
        the coordinates of each point defining the polygon)

    Note that filtering on activity types should occur prior to using contains, because given an
    object instance, we don't know what activity types it is associated to.
    """
    def __init__(self, video_files, frames, activity_types, points, thd="10p"):
        self.videos = video_files
        self.frames = frames
        self.types = activity_types
        self.points = points
        self.thd = thd
        self.filter = self._build_filter()


    def _build_filter(self):
        """
        Return a filter function. It says whether an instance has to be ignored or not.
        Note: f is optional in the frame_pattern because it is the default behavior,
        so it should be checked lastly.
        """
        percentage_pattern = r'^([0-9]+)p$'
        frame_pattern = r'^([0-9]+)f?$'

        if re.match(percentage_pattern, self.thd):
            v = int(re.findall(percentage_pattern, self.thd)[0])

            def _filter(c, t):
                return c / t >= v
        elif re.match(frame_pattern, self.thd):
            v = int(re.findall(frame_pattern, self.thd)[0])

            def _filter(c, t):
                return c >= v

        return _filter


    def contains(self, obj):
        """
        `obj` is supposed to be a ObjectLocalizationInstance in the scorer.
        It is gonna be a dict for this POC
        Return True if self (the DNA) contains obj. If so, that mean `obj` should not
        be included during the scoring process.
        """
        def is_inside(centroid):
            # Ray casting algorithm
            # https://en.wikipedia.org/wiki/Point_in_polygon#Ray_casting_algorithm
            n = len(self.points)
            # Create a point for line segment
            # from p to infinite
            extreme = (9999099999999, centroid[1])
            count = i = 0
            while True:
                next = (i + 1) % n
                # Check if the line segment centroid to
                # extreme intersects with the line
                # segment from 'polygon[i]' to 'polygon[next]'
                if intersect(self.points[i], self.points[next], centroid, extreme):
                    # If centroid is collinear with line segment 'i-next',
                    # then check if it lies on segment. If it lies,
                    # return true, otherwise false.
                    if orientation(self.points[i], centroid, self.points[next]) == 0:
                        return segment(self.points[i], centroid, self.points[next])
                    count += 1
                i = next
                if (i == 0):
                    break

            # Return true if count is odd, false otherwise
            return (count % 2 == 1)

        # Not the same video
        video = list(obj['localization'].keys())[0]
        if video in self.videos is None:
            return False

        loc = obj['localization'][video]
        obj_frames = sorted(map(lambda x: int(x), loc.keys()))

        # Not on the same timespan
        if min(obj_frames) > self.frames[1] or max(obj_frames) < self.frames[0]:
            return False

        # From that point we know the object and the DNA temporally overlaps
        # We now need to identify the temporal signal

        obj_frames_count = len(obj_frames)

        def _check(count):
            return self.filter(count, obj_frames_count)

        # count is the number of frames that have their object centroid inside the DNA 
        count = 0
        inter = inter_list(obj_frames, self.frames)
        for i in range(len(inter)-1):
            frame = inter[i]
            try:
                bbox = loc[frame]["boundingBox"]
            except KeyError:  # May happend if frame is not defined for the object ; hopefully the previous one is
                frame = str(max(x for x in obj_frames if x < int(frame)))
                bbox = loc[frame]["boundingBox"]

            bbox_centroid = centroid(bbox)
            # if the centroid is inside the polygon, count this frame as TP
            inside =  is_inside(bbox_centroid)
            if inside:
                count += int(inter[i+1]) - int(frame)
            # For optimization, interrupting asap
            if _check(count):
                return True
        return False
