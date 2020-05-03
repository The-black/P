# Devops scripting task submission

This folder contains my submission of the devops scripting task.

## The task:
Consider that you have a drive with millions of files & folders.
Some of the items are duplicates of each over. (duplicate content, not the name)
Some of them are several GB in size.

Print a list of all files names that are duplicates of each other in the same line separated by a comma.
If the file does not have duplicates - do not print its name 

You should come up with the best algorithm possible to perform this task.
Write clean code
You can use any programing language you wish.



## Submission:
This task is submitted as a single python 3 file:

| Filename | Description |
| ------ | ------ |
| [listDupes.py](listDupes.py) | List duplicate files, each set of duplicates in a single comma-separated line  |
| [README.md](README.md) | This documentation file |


## Prerequisites and assumptions
  - Python 3 is installed and functional
  - The running user has sufficient permissions 
  - Host has sufficient resources for running the script (memory usage and number of open files are configurable at the top of the script)

## Checking the task:
Download **[listDupes.py](listDupes.py)**, then run:

`$ time python3 ./listDupes.py <workdir> [<another dir> ...]`

- Scanning multiple directories is support them, specify the list at the command line (space separated)
- Output is printed to stdout and can be redirected any way you want
- Errors are sent to stderr
- If running with no parameters, usage is printed to stderr

## Optimizations employed in the code:

 - Only compare files of the same size
 - Do not read a file more than once
 - For large files, perform hash of sample blocks before going into full scan. Sample blocks include the beginning and end of the files, as well as evenly-spread blocks along it
 - Magnetic and Electronic media use different optimizations. For Magnetic media the algorythm reduces seek operations whereas for electronic media the algorythm reduces the amount of data being read. Type is determined by **mediaType**
  - When a file is found to be unique, remove it from the compare list so it will not be read entirely for no good reason (Electronic media)
  - When there are less remaining files to compare than the defined max open files, leave their file handles open (Electronic media)
  - When there are more remaining files to compare than the defined max open files, allow for increasing the block size (Note memory restrictions, electronic media)
  - Using loops for reading rather than recursion, as recursion could get too deep with huge files, though recursion could improve efficiency when there a many (above max open) files.



Enjoy :)

  Nadav.

