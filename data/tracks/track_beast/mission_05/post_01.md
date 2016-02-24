## Unknown wiki

One of our informers learned that we would need a particular piece of information in order to disable some of the dome's
security mechanisms. Unfortunately, we lost all of his report. All we know is that he pointed us towards an article on
a famous wiki of the old era. The only extra information we have is this bit of Perl.


```
perl -ne 'print if(("x"x$_)!~/^(..+)\1+$/);'
```

**Objectives:** Find the url of the wiki page he was talking about.

**Notes:** The flag is in the standard format.
