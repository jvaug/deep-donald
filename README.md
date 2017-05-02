# deep-donald

[@DeepDonald_](https://twitter.com/DeepDonald_)

### Question

The purpose of this project was to create a self-contained Twitter bot that could take some seed text in the form of a tweet and respond in the style of Donald Trump.

### Data Collection and Cleaning

A complete archive of Trump's tweets was readily available thanks to the work of [bpb27](https://github.com/bpb27/trump-tweet-archive) who maintains http://www.trumptwitterarchive.com/.  The key fields contained in the JSON formatted files were 'source' (the device used to send the tweet) and 'text' (the tweet's content). 

We know that not all Trump tweets are created equal; thanks to the work of [David Robinson](http://varianceexplained.org/r/trump-tweets/) (and others), we know tweets sourced from 'Twitter for Android' are from the Donald himself and not a staffer.

Taking this into account, we were left with a trimmed down corpus of roughly ~15k tweets out of the ~31k total available.  This was further reduced to ~7k with the removal of any "old-school retweet" tweets.  These follow the format of "RT@USER..." response.  Since most of the text in these tweets is from other Twitter users and not Trump, they would not be useful for training our model.

Additional text was gleaned from several interviews and speech transcripts (AP, CBS, etc).  The total aggregate corpus for training was 1.5 MB.

The speech transcripts were mostly cleaned by hand as they presented many unique challenges.  The data had many artifacts, interviewer questions and comments had to be removed, and markers for applause/laughter/etc had to be removed.  

These steps were laborious but necessary to make sure the model output was as high quality as possible.  Poorly cleaned/standardized inputs led to poor output initially; time spent on this step paid the highest dividends toward the final product.

### Features

For the traditional modeling portion of this project, TF-IDF vectorization was used for feature generation.  Because this type of vectorization emphasizes the importance of rarer words, it gives us the most empirically useful data for classification.

### Modeling

Recurrent neural network - used RNN implementation in Torch https://github.com/jcjohnson/torch-rnn.  We used character level so that user inputs wouldn't have to be limited to words already present in the corpus (we can use model to generate output on topics trump has never spoken about before this way).

Model was trained with 3 layers, 512 nodes.

Tweet classifying model is a voting classifier estimator running with a logistic regression, random forest and extra trees model.  The base model score was .15 while the test score was .89, indicating a very significant improvement via modeling.  The models and TF-IDF transformer were pickled to allow easy implementation in the twitter response script.

### Conclusions



### Future Direction

