## Unknown Directive

One of our informers learned that we would need a particular piece of information in order to disable some of the dome's security mechanisms thus give us some directives to bypass the system.

Unfortunately, we lost all of his report. All we remember is this little bit of Perl.


```
perl -ne 'print if(("x"x$_)!~/^(..+)\1+$/&&1<$_);'
```

And this strange text.

```
UQAM\{[a-z]{5} [a-z]{6}\}
```

**Objectives:** Find what he was talking about.
