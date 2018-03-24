selfish
======
Making 'self' implicit, because even Java did a better job at this.


### Install
```pip install selfish```


### Usage
```
@selfish
class Foo():
    def __init__(val): self.val = val

    def val(): return self.val

    @classmethod
    def klass(): return self


Foo(1).val()
> 1

Foo.klass()
> Foo
```
