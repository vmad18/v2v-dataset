# v2v-dataset (w.i.p.)
preprocessing code for creating a diverse video dataset

Currently in development more features and code polishing will be done in time.

# how to use

* Download TF-records from [here](https://research.google.com/youtube8m/download.html)
* Place TF-records into  records  directory

```bash
python3 main.py --contents (t/true/1/nothing) --video (t/true/1/nothing)
```
* Arguments
  * contents  will save all TF-record data to file
  * video  will save all video urls from TF-record data to file
