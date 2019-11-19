#!#/usr/bin/gnuplot

set term pdf
set out "densPlot.pdf"

print "Generating plots"

set title "Energy vs \# DB entries (binwidth 1keV) "
set xlabel "Energy [keV]"
set ylabel "Number of DB entries"

# plot "dens4Plotting.txt" smooth freq with boxes
plot "dens4Plotting.txt" w l

set out "densPlotLog.pdf"
set log y

replot
