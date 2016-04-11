# Negation Resolution

An NLP tool that performs Negation resolution on sentences. It takes as input a sentence and a target-keyword. It returns `True` for affirmed keywords, `False` for negated and `None` for keywords not found.

## Installation

1. Download and extract [CoreNLP](http://stanfordnlp.github.io/CoreNLP/#download). 
2. Install [stanford_corenlp_pywrapper](https://github.com/brendano/stanford_corenlp_pywrapper)
3. Install through ```requirements.txt```:
	```
	pip install -r requirements.txt
	```
4. Edit ```settings.json```. Make sure you keep the leading slashes in the directory names.

##Example

```bash
cd negation-detection
```
```python
import negation_detection
sentence = "The patient is suicidal"
negation.predict(sentence, 'suicide')
```

## Reference
George Gkotsis, Sumithra Velupillai, Anika Oellrich, Harry Dean, Maria Liakata and Rina Dutta. Don't Let Notes Be Misunderstood: A Negation Detection Method for Assessing Risk of Suicide in Mental Health Records, Computational Linguistics and Clinical Psychology. 2016