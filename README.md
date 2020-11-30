# Kriptografi-Tubes-2

# Notes Bug Fix
In `lib/python<version>/site-packages/django/forms/boundfield.py`, remove line `renderer` params in widget.render call.

See code below for reference
```
return widget.render(
    name=self.html_initial_name if only_initial else self.html_name,
    value=self.value(),
    attrs=attrs,
)
# renderer=self.form.renderer,
```

Source: [render() got unexpected keyword renderer](https://github.com/froala/django-froala-editor/issues/55)
