# Negation Resolution

An NLP tool that performs Negation resolution on sentences. It takes as input a sentence and a target-keyword. It returns `True` for affirmed keywords, `False` for negated and `None` for keywords not found.

## Installation

First you need to download and extract [CoreNLP](http://stanfordnlp.github.io/CoreNLP/#download). 

Follow requirements.txt:

```shell
pip install -r requirements.txt
```

Edit settings.json. Make sure you keep the leading slashes in the directory names.

##Example

```python
import negation
sentence = "The patient is suicidal"
negation.predict(sentence, 'suicide')
```


