# Duplicate image detector

OpenCV-based duplicate image detector. 

## Prerequisites
```
pip3 install -r requirements.txt 
```

### Raspberry Pi
For running this script on a Raspberry Pi, the following additional libraries need to be installed:
```
sudo apt install libcblas-dev libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev libqtgui4 libqt4-test
```
Source: https://stackoverflow.com/a/53402396


## Unit tests
```
python3 -m unittest discover -v -s ./tests
```

### Coverage

- Run coverage scan
  ```
  python3 -m coverage --source=src/ run -m unittest discover -s ./tests
  python3 -m coverage run -m unittest discover -s ./tests
  ```
- View coverage report
  ```
  ./coverage_report.sh
  ```


## TODO's: 
- [ ] Add more tests
- [ ] Improve type hinting 
- [ ] store keypoints, features in SQLite DB
- [ ] extract relevant part; remove BG