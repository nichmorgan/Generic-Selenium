# Generic-Selenium
Generic class for selenium web automation in python dedicated to providing efficient optimizations for diverse use in web automation.

## Class Call
```python
def __init__(self, username, password, homeUrl, downloadFolder, autoGuiPicsFolder, driverFolder, driver)
```
Drivers initialization according to webdriver's specific type, plus loading configuration profiles.  
- *username and password*: for systems requiring access management, **to ignore use empty string**;
- *homeUrl*: home page, recommended for login for pages with user access;
- *downloadFolder*: Determines where to download files while they are running;
- *autoGuiPicsFolder*: Determines the folder in which pyautogui usage images are contained. Used in internet explorer;
- *driverFolder*: determines the folder in which webdrivers are contained;
- *driver*: determines which webdriver to use, the current options being **Chrome, Firefox32, Firefox64, Ie32 and Ie64**.  

## Operation History Handler
```python
def _manipule_data_fields(self, key, value)
```
Stores the sub-level key dictionary: current and last. Must be used to change values inherent in the processes executed.  
- *key*: key to be stored;
- *value*: current value to be stored. If a current value already exists, it will be stored as last.<br/><br/>

```python
def _get_data_fields(self, key)
```
Returns the previous and current values, in this order.<br/><br/>

```python
def _update_process(self, process)
```
Stores in the history dictionary the current process using the *manipule_data_fields* function.
- *process*: process name.

## File operators
```python
def _getNewestFile(self, dirPath)
```
Returns the most recent file path in the directory *dirPath*.<br/><br/>

```python
def _moveFile(self, pFrom, pTo)
```
Move and / or rename * pFrom * file to * pTo *:
- Move: **pTo** must be a folder and the file name will be that contained in **pFrom**;
- Move and rename: * pTo * must contain file name to be renamed.<br/><br/>

```python
def _saveSourceAsPDF(self, url, outputPath = None)
```
Saves a page as a PDF file in a given directory or download folder determined in the class call.
- *url*: web address to save, not need to be the current page;
- *outputPath*: Save location, if not determined will be used the given download directory.<br/><br/>

