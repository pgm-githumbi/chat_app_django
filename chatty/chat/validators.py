
from abc import ABC
import re
import bleach

class BaseValidator:
    def is_valid(self, value, context=None):
        return NotImplemented
    
class BaseCleaner(ABC):
    def __init__(self, value = None, base_cleaner: 'BaseCleaner' = None):
        self.value:'str' = value
        if base_cleaner is not None:
            self.value = base_cleaner.clean()

    def clean(self):
        raise NotImplementedError("Not implemented")
    

class ChannelGroupValidator(BaseValidator):
    def is_valid(self, value, context=None):
        # Regular expression pattern to match allowed characters
        pattern = r'^[a-zA-Z0-9_\-.]+$'
        
        # Check if the input string matches the pattern
        return re.match(pattern, value) is not None
    
class BasicCleaning(BaseCleaner):
    def clean(self,):
        # remove leading and trailing whitespace
        string = self.value.strip()
        # replace consecutive whitespace with single space
        string = " ".join(string.split())
        # escape single quotes
        string = string.replace("'", "\\'")
        return string
    

class HtmlSanitizer(BaseCleaner):
    def __init__(self, *args,**kwargs,):
        super().__init__(*args, **kwargs,)
        self.setup()
        
    def setup(self, allowed_tags=[], allowed_attributes=dict()):
        self.allowed_tags = allowed_tags
        self.allowed_attributes = allowed_attributes
        return self

    def clean(self):
        return bleach.clean(self.value, tags=self.allowed_tags,
                      attributes=self.allowed_attributes)

    