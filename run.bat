@echo off
set start=%time%
python materials.py
set end=%time%
echo Start Time: %start%
echo End Time:   %end%
@pause
