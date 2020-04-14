#!/usr/bin/env perl

# Check we have every module (perl wise)
my (@f4bv, $f4d);
BEGIN {
    use Cwd 'abs_path';
    use File::Basename 'dirname';
    $f4d = dirname(abs_path($0));

    push @f4bv, ("$f4d/../../../common/lib");
}
use lib (@f4bv);

use AutoTable;
use Getopt::Long;
use MMisc;
#use Data::Dumper;

Getopt::Long::Configure(qw( auto_abbrev no_ignore_case));

my $out_type = "Txt";
my $sort_row = "AsAdded";
my $sort_row_key = "";
my $sort_col = "AsAdded";
my $sort_col_key = "";
my $separator = '\s';
my $prefix_text = "";
my $properties = {};
my $strip_whitespace = undef;
my $transpose = undef;

GetOptions
(
 'append:s' => \$prefix_text,
 'type:s' => \$out_type, 
 'row-sort:s' => \$sort_row,
 'col-sort:s' => \$sort_col,
 'separator:s' => \$separator,
 'Strip-whitespace' => \$strip_whitespace,
 'properties:s@' => \$props,
 'list-props' => sub { MMisc::ok_quit(&list_properties); },
 'Transpose' => \$transpose,
 'help' => sub { MMisc::ok_quit(&get_usage); },
) or MMisc::error_quit("Unknown option(s)\n".&get_usage);

#Format out type options as understood by AutoTable, and setup render
#specific property keys
if ($out_type =~ /te?xt/i) { 
    $out_type = "Txt";
    $sort_row_key = "SortRowKeyTxt";
    $sort_col_key = "SortColKeyTxt";
} elsif ($out_type =~ /csv/i) { 
    $out_type = "CSV";
    $sort_row_key = "SortRowKeyCsv";
    $sort_col_key = "SortColKeyCsv";
} elsif ($out_type =~ /html/i) { 
    $out_type = "HTML"; 
    $sort_row_key = "SortRowKeyHTML";
    $sort_col_key = "SortColKeyHTML";
} elsif ($out_type =~ /latex/i) { 
    $out_type = "LaTeX"; 
    $sort_row_key = "SortRowKeyLaTeX";
    $sort_col_key = "SortColKeyLaTeX";
} else { MMisc::error_quit("Unrecognized type '$out_type'") }

my $at = new AutoTable();

foreach my $prop(@$props) {
    my ($k, $v) = split(/:/, $prop);
    $properties->{$k} = $v;
}

foreach my $prop(keys %$properties) {
    if ($prop eq "separator") {
	$separator = $properties->{$prop};
    } else {
	unless ($at->{Properties}->setValue($prop, $properties->{$prop})) {
	    print &property_error();
	}
    }
}

#Set properties from options
if ($prefix_text) {
    unless ($at->{Properties}->setValue("TxtPrefix", $prefix_text)) {
	print &property_error();
    }
}
unless ($at->{Properties}->setValue($sort_row_key, $sort_row)) {
    print &property_error();
}
unless ($at->{Properties}->setValue($sort_col_key, $sort_col)) {
    print &property_error();
}

while (<STDIN>){
    chomp;
    my @a;
    if ($separator eq "\\s" || $separator eq " "){
      s/^\s+// if ($strip_whitespace);
      @a = split(/$separator/);
    } else {
      @a = split(/$separator/);
      if ($strip_whitespace) {
	for (my $i=0; $i<@a; $i++) {
	  $a[$i] =~ s/^\s*(.*?)\s*$/$1/
	}
      }
    }
    if (!defined $transpose){   
	$at->addData($a[0], $a[1], $a[2]);
	$at->setSpecial($a[1], $a[2], $a[3]) if (@a > 3);
    } else {
	$at->addData($a[0], $a[2], $a[1]);
	$at->setSpecial($a[2], $a[1], $a[3]) if (@a > 3);
    }
}

#Render
my $rendered_at = "";
if ($out_type eq "Txt") {
    $rendered_at = $at->renderTxtTable(1);
} elsif ($out_type eq "HTML") {
    $rendered_at = $at->renderHTMLTable(1);
} elsif ($out_type eq "LaTeX") {
    $rendered_at = $at->renderLaTeXTable();
} elsif ($out_type eq "CSV") {
    $rendered_at = $at->renderCSV();
} else {
    MMisc::error_quit("I need a Renderer for now '$out_type'");
}
if ($rendered_at) {
    print $rendered_at;
} else {
    MMisc::error_quit("Didn't render anything, aborting");
}

sub property_error {
    $at->{Properties}{errormsg}->errormsg()."\n";    
}

sub list_properties {
    my $at = new AutoTable();
    $at->{Properties}->printShortPropList();
    return;
}

sub get_usage {
    return <<'EOT';

TableMan.pl [ OPTIONS ]
    
    -t, --type        Output type of generated AutoTable possible
                      types are (Txt|HTML|LaTeX|CSV) default is Txt.
    -r, --row-sort    Sorts rows by either (Alpha|Num|AsAdded) default
                      is AsAdded.
    -c, --col-sort    Sorts columns by either (Alpha|Num|AsAdded)
                      default is AsAdded.
    -s, --separator   Field separator for input file default is space.
    -S, --strip_whitespace
                      Removes leading and trailing whitespace from
              each field.
    -a, --append      Append text to each line when rendering in text
                      mode, useful for indentation.
    -p, --properties  Specify properties as a list of property:value
                      pairs.
    -l, --list-props  List accepted properties and values.
    -T, --Transpose   Transpose the table by swaping colums 2 and 3

    -h, --help        Print this usage text.


Example Usage:

(echo "v1 col1|s1 row1|r1"; echo "v2 col1|s2 row1|r1"; echo "v3 col1|s1 row1|r2"; echo "v4 col2|s1 row1|r12"; ) | TableMan


EOT
}

exit 0;
