# deep-donald

### INCOMPLETE

Neural network Trump twitter auto-reply bot

@DeepDonald_

Question

The purpose of this project was to create a self-contained Twitter bot that could take seed text in the form of a tweet and respond in the style of Donald Trump.

Background

Throughout Trump's 2016 presidential campaign, he gained a reputation as a 

Data Collection and Cleaning

A complete archive of Trump's tweets was readily available thanks to the work of https://github.com/bpb27/trump-tweet-archive who maintains http://www.trumptwitterarchive.com/.

We also know that not all Trump tweets are created equal; thanks to the work of David Robinson @ http://varianceexplained.org/r/trump-tweets/ (and others), we know tweets sourced from 'Twitter for Android' are from the Donald himself and not a staffer.

This led to a trimmed down corpus of roughly ~15k tweets out of the ~31k total available.  I further reduced this number to ~7k when I decided to remove any "old-school retweet" tweets.  These follow the format of "RT@USER..." response.  Since most of the text in these tweets is from other twitter users, I did not think they would be useful for training our model.

Additional text was gleaned from several interviews and speech transcripts (AP, CBS, etc).  The total aggregate corpus for training was 1.5 MB.

Speech transcripts were mostly cleaned by hand.  The data had many artifacts, interviewer questions had to be removed, markers for applause/laughter etc had to be removed.  This was laborious but necessary to make sure the model output was as high quality as possible.

Features

For the traditional modeling portion of this project, TF-IDF vectorization was used for feature generation.  No additional features were added because output tweets would only have their text to go on.


Exploratory Data Analysis



Modeling

Recurrent neural network - used RNN implementation in Torch https://github.com/jcjohnson/torch-rnn.  We used character level so that user inputs wouldn't have to be limited to words already present in the corpus (we can use model to generate output on topics trump has never spoken about before this way).

Model was trained with 3 layers, 512 nodes.

Tweet classifying model is a voting classifier estimator running with a logistic regression, random forest and extra trees model.  The base model score was .15 while the test score was .89, indicating a very significant improvement via modeling.  The models and TF-IDF transformer were pickled to allow easy implementation in the twitter response script.

Conclusions



Future Direction

