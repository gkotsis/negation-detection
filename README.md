# Negation Resolution

An NLP tool that performs negation resolution on a sentence level. It takes as input a sentence and a target-keyword. It returns `True` for affirmed keywords, `False` for negated and `None` for keywords not found. The tool makes use of Stanford's CoreNLP constituency trees.

## Installation

1. ```git clone https://github.com/gkotsis/negation-detection```
2. Download and extract [CoreNLP](http://stanfordnlp.github.io/CoreNLP/#download). 
3. Install [stanford_corenlp_pywrapper](https://github.com/brendano/stanford_corenlp_pywrapper)
4. Install through ```requirements.txt```:
	
	```
	cd negation-detection
	pip install -r requirements.txt
	```
5. Edit ```settings.json```. Make sure you keep the leading slashes in the directory names.

##Example

```python
import negation_detection
sentence = "The patient is suicidal"
negation.predict(sentence, 'suicide')
```

## Reference
George Gkotsis, Sumithra Velupillai, Anika Oellrich, Harry Dean, Maria Liakata and Rina Dutta. Don't Let Notes Be Misunderstood: A Negation Detection Method for Assessing Risk of Suicide in Mental Health Records, Computational Linguistics and Clinical Psychology. 2016