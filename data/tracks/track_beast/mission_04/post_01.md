# Mission Order

The following piece of code seems to be the lock that checks the master administrator password of the sea food storage.

```
perl -ne 'chomp;print"FLAG:$_\n"if(/^(?=[b-k]*$).(?!.[e-])((.).)(?:\1)*\2(?<=[^c-z][^querty][^e-z][aeiouy][d-z]{2})(?(1).{7,8}z*$|f*^)$/);'
```

This looks like some randomely generated gibberish but maybe this is some hidden gem inside.

**Mission Type:** Oyster farming

**Objectives:** Find the password.
