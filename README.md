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
python -m unittest discover -v -s ./tests
```

### Coverage

- Run coverage scan
  ```
  python -m coverage run -m unittest discover -s ./tests
  ```
- View coverage report
  ```
  ./coverage_report.sh
  ```


## TODO's: 
- [ ] Use poetry for dependency management: https://python-poetry.org/
- [ ] Add more docblocks
- [ ] Add more tests
- [ ] Improve type hinting 
- [ ] Use "fire" for CLI app: https://towardsdatascience.com/a-simple-way-to-create-python-cli-app-1a4492c164b6