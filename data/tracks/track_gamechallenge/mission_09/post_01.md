## Nonogram madness

We have uncovered the description of an old-era style puzzle during an expedition of the scouting legion.

It apparently describes what was once a great threat to lifeforms in the galaxy.

Can you solve the puzzle and send us the name of said creature ?

The file appears to be split in two sections, separated by a '-' token:

* The first part represents the column constraints
* The second part represents the line constraints

If we took the example of such a file for a simple figure, it would look like this:

~~~
0 0 1 1 0
1 2 1 1 5
-
0 1
0 2
1 1
1 1
0 5
~~~

And would yield the following image:

~~~
    *
   **
  * *
 *  *
*****
~~~

[This](nonogram.txt) is the input file we were given.

### Objectives

Find the name of the life-threatening creature hidden by the nonogram puzzle (formatted as UQAM{name})
