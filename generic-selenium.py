#coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import os
import re
import pyautogui
import base64

from winreg import *

class GenericSelenium:
	def __init__(self, username, password, homeUrl, downloadFolder, autoGuiPicsFolder, driverFolder, driver):
		assert os.path.isdir(os.path.abspath(driverFolder)), "[GenericSelenium | __init__] The driver folder must be a directory."
		driverFolder = os.path.abspath(driverFolder)
		
		self.downloadFolder = downloadFolder

		self.__indexJSArg = 0
		if driver == "Chrome":
			self.__driverType = "Chrome"
			driver = webdriver.Chrome(os.path.join(driverFolder,"chromedriver.exe"))
		elif "Firefox" in driver:

			fp = webdriver.FirefoxProfile()
			fp.set_preference("browser.shell.checkDefaultBrowser", False)
			# lock update
			fp.set_preference("app.update.enabled", False)
			fp.set_preference("app.update.auto", False)
			fp.set_preference("app.update.mode", 0)
			fp.set_preference("app.update.service.enabled", False)
			# prevent close warnings
			fp.set_preference("browser.showQuitWarning", False)
			fp.set_preference("browser.warnOnQuit", False)
			fp.set_preference("browser.tabs.warnOnClose", False)
			fp.set_preference("browser.tabs.warnOnCloseOtherTabs", False)
			# Download configs
			fp.set_preference("browser.download.folderList",2)
			fp.set_preference("browser.download.manager.showWhenStarting",False)
			fp.set_preference("browser.download.dir", self.downloadFolder)
			fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
			fp.set_preference("browser.helperApps.neverAsk.openFile", "application/pdf")
			fp.set_preference("browser.download.panel.shown", False)
			fp.set_preference("pdfjs.disabled", True)

			# Hide Images
			fp.set_preference('permissions.default.image', 2)
			fp.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', False)

			if driver == "Firefox64":
				self.__driverType = "Firefox"
				capabilities = webdriver.DesiredCapabilities().FIREFOX
				capabilities["marionette"] = True
				#binary = webdriver.firefox.firefox_binary.FirefoxBinary(os.path.join(driverFolder, "geckodriver_64.exe"))
				driver = webdriver.Firefox(executable_path=os.path.join(driverFolder, "geckodriver_64.exe"),
					capabilities=capabilities, firefox_profile=fp)
			else:
				self.__driverType = "Firefox"
				capabilities = webdriver.DesiredCapabilities().FIREFOX
				capabilities["marionette"] = True
				#binary = webdriver.firefox.firefox_binary.FirefoxBinary(os.path.join(driverFolder, "geckodriver_32.exe"))
				driver = webdriver.Firefox(executable_path=os.path.join(driverFolder, "geckodriver_32.exe"),
					capabilities=capabilities, firefox_profile=fp)
			
		elif driver == "Ie32":
			self.__driverType = "Ie"
			self._oHideBrowserImages()
			driver = webdriver.Ie(os.path.join(driverFolder,"IEDriverServer_32.exe"))
		elif driver == "Ie64":
			self.__driverType = "Ie"
			self._oHideBrowserImages()
			driver = webdriver.Ie(os.path.join(driverFolder,"IEDriverServer_64.exe"))
		else:
			raise Exception("Nenhum driver válido foi determinado")
		
		self.__driver = driver
		self.__homeURL = homeUrl
		self.__data_fields = {}

		self.__autoGuiPicsFolder = os.path.abspath(autoGuiPicsFolder) if not autoGuiPicsFolder is None else None

		self.__logged = False

		self.username = username
		self.password = password
		
	# Operation History Handler
	def _manipule_data_fields(self, key, value):
		if key in self.__data_fields.keys():
			self.__data_fields[key]["last"] = self.__data_fields[key]["actual"]
			self.__data_fields[key]["actual"] = value
		else:
			self.__data_fields[key] = {"last":None, "actual":value}
			
	def _get_data_fields(self, key):
		if key in self.__data_fields.keys():
			return self.__data_fields[key]["last"], self.__data_fields[key]["actual"]
		else:
			return "", ""

	def _update_process(self, process):
		self._manipule_data_fields("process", process)
	
	# Thanks for Marlon Abeykoon and jmlarson for the help in StackOverflow.
	# url: https://stackoverflow.com/a/39327156/12294698
	def _getNewestFile(self, dirPath):
		dirPath = os.path.abspath(dirPath)
		assert os.path.isdir(dirPath), "[GenericSelenium | _getNewestFile] The dir path must be a directory path."
		list_of_files = glob.glob(dirPath) # * means all if need specific format then *.csv
		latest_file = max(list_of_files, key=os.path.getctime)
		return latest_file

	def _moveFile(self, pFrom, pTo):
		assert os.path.isfile(pFrom), "[GenericSelenium | _moveFile] The from path file is invalid."
		pFrom = os.path.abspath(pFrom)

		if os.path.isdir(pTo):
			pTo = os.path.join(os.path.abspath(pTo), os.path.basename(pFrom))
		elif os.path.isdir(os.path.dirname(pTo)):
			pTo = os.path.abspath(pTo)
		else:
			raise Exception("[GenericSelenium | _moveFile] The to path file is invalid.")

		os.rename(pFrom, pTo)
	
	# Thanks for Marcelo Betiati for the help with js script
	def _saveSourceAsPDF(self, url, outputPath = None):
		script = """
			var retornoJavascript = arguments[0];
			//Javascript para chamar Download do PDF
			var request =  new XMLHttpRequest();
			request.open('GET','%s');
			request.responseType='arraybuffer';
			request.onload = function(e) {
				var file = new Blob([this.response],{type:'application/octet-stream'});
				//window.navigator.msSaveOrOpenBlob(file, 'testeJs.pdf');
				
				var reader = new FileReader();
				reader.readAsDataURL(file);
				reader.onloadend = function() {
					var base64data = reader.result;
					retornoJavascript(base64data);
				}
			};
			request.send();
		""" % url

		pdfFile = self.driver.execute_async_script(script)

		if outputPath is None:
			outputPath = os.path.join(self.downloadFolder, "file.pdf")

		assert not os.path.isdir(outputPath) and os.path.isdir(os.path.dirname(outputPath)), "[GenericSelenium | _saveSourceAsPDF] Output path is invalid."
		with open(outputPath, "wb") as f:
			f.write(base64.b64decode(pdfFile))
			f.close()
	
	# web operators
	def _oWaitSendKeys(self, element, text, waitTime=0, regexFormat=None):
		print("\n\n _oWaitSendKeys")
		element.clear()
		element.send_keys(str(text))
		
		text = str(text).replace("\ue003", "")

		if regexFormat is None:
			compareFunc = lambda txtinput: element.get_attribute("value").lower() == text.lower()
		else:
			def func(txt):
				return re.sub(regexFormat, "", element.get_attribute("value")).lower() == re.sub(regexFormat, "", text.lower())
			compareFunc = func

		WebDriverWait(self.__driver, waitTime).until(compareFunc)

	def _oWait2FindAndClick(self, by, textID, waitTime=0, validator=None, validatorValue=None, tryies=2, regex=False):
		print("\n_oWait2FindAndClick")
		tryed = 0
		success = False
		for tryed in range(tryies):
			if waitTime > 0:
				WebDriverWait(self.__driver, waitTime).until(
					EC.presence_of_element_located((by,str(textID)))
					).click()
			else:
				self.driver.find_element(by,textID).click()

			if validator is None:
				success = True
				break
			else:
				assert len(validator) in [2,3], f"[GenericSelenium | _oWait2FindAndClick] validator length ({len(validator)}) is invalid."
				validatorWaitTime = 3 if len(validator) < 3 else validator[2]
				if validatorValue is None:
					if self._oHasElement(validator[0], validator[1], validatorWaitTime) == True:
						success = True
						break

					assert len(validatorValue) == 2, f"[GenericSelenium | _oWait2FindAndClick] validator length ({len(validatorValue)}) is invalid."
					if regex == False:
						if self._oHasElement(validator[0], validator[1], validatorWaitTime, validatorValue[0]) == validatorValue[1]:
							success=True
							break
					else:
						if re.search(validatorValue[1], self._oHasElement(validator[0], validator[1], validatorWaitTime, validatorValue[0])):
							success=True
							break


		if success==False:
			raise Exception("[GenericSelenium | _oWait2FindAndClick] Max tryies of validation error.")
			
	def _oWait2FindAndSendKeys(self, by, textID, textEntry, waitTime=0, regexFormat=None):
		print("\n_oWait2FindAndSendKeys")
		print(by,textID, textEntry)
		if waitTime > 0:
			element = WebDriverWait(self.__driver, waitTime).until(EC.presence_of_element_located((by,str(textID))))
		else:
			element = self.driver.find_element(by,textID)
		
		self._oWaitSendKeys(
			element=element,
			text=str(textEntry),
			waitTime=10,
			regexFormat=regexFormat,
		)

	def _oHasElement(self, by, textID, waitTime=0, attribute=None, multiple=False):
		try:
			if multiple == False:
				if waitTime > 0:
					element = [WebDriverWait(self.__driver, waitTime).until(
						EC.presence_of_element_located((by,str(textID)))
						)]
				else:
					element = [self.driver.find_element(by,textID)]
			else:
				if waitTime > 0:
					element = WebDriverWait(self.__driver, waitTime).until(
						EC.presence_of_all_elements_located((by,str(textID)))
						)
				else:
					element = self.driver.find_elements(by,textID)

			if attribute is None:
				return True
			else:
				try:
					if attribute == "all_element":
						output = [e for e in element]
					else:
						output = [e.get_attribute(attribute) for e in element]

					if multiple == True:
						return output
					else:
						return output[0]
				except:
					raise Exception("[GenericSelenium | _oHasElement] Attribute not found.")
		except Exception as e:
			print(e)
			return False
		
	def _oWait2GetAllUrlElements(self, url, waitTime=60):
		self.__driver.get(url)
		WebDriverWait(self.__driver, waitTime).until(EC.presence_of_all_elements_located)
		
	def _oClickSaveButton(self):
		assert os.path.isdir(self.autoGuiPicsFolder), "[GenericSelenium | _oClickSaveButton] autogui pics folder is invalid."
		assert os.path.isfile(os.path.join(self.autoGuiPicsFolder,"saveButton.png")), "[GenericSelenium | _oClickSaveButton] autogui saveButton.png not found."
		
		saveButton = pyautogui.locateCenterOnScreen(os.path.join(self.autoGuiPicsFolder,"saveButton.png"))
		pyautogui.click(saveButton)

	def _oChangeDownloadDirectory(self, downloadFolder):
		if self.__driverType == "Ie":
			key = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Internet Explorer\Main", 0, KEY_ALL_ACCESS)
			SetValueEx(key, "Default Download Directory", 0, REG_SZ, downloadFolder)
			CloseKey(key)

	def _oHideBrowserImages(self):
		if self.__driverType == "Ie":
			key = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Internet Explorer\Main", 0, KEY_ALL_ACCESS)
			SetValueEx(key, "Display Inline Images", 0, REG_SZ, "no")
			CloseKey(key)

	def _oCloseBrowser(self):
		if self.__driverType == "Ie":
			self.driver.quit()
		else:
			self.driver.close()
		
	@property
	def driver(self):
		return self.__driver

	@property
	def last_process(self):
		return self.__data_fields["process"]["last"]

	@property
	def actual_process(self):
		return self.__data_fields["process"]["actual"]

	@property
	def logged(self):
		return self.__logged
		
	@property
	def username(self):
		return self.__username
		
	@property
	def password(self):
		return self.__password
	
	
	@property
	def homeURL(self):
		return self.__homeURL
		
	@property
	def driverType(self):
		return self.__driverType

	@property
	def autoGuiPicsFolder(self):
		return self.__autoGuiPicsFolder

	@property
	def downloadFolder(self):
		return self.__downloadFolder
	
	# Setters
	
	def __stringSetter(self, value):
		try:
			value = str(value)
		except:
			raise Exception("[GenericSelenium | __stringSetter] The value fails in string conversion.")
		assert len(value) > 0, "[GenericSelenium | __stringSetter] The value length must be greater than 0."
		
		return value
	
	@username.setter
	def username(self, value):
		self.__username = self.__stringSetter(value)
		
	@password.setter
	def password(self, value):
		self.__password = self.__stringSetter(value)
		
	@logged.setter
	def logged(self, value):
		assert type(value) == type(True), "[GenericSelenium | logged.setter] The value must be a boolean type."
		self.__logged = value
	
	@homeURL.setter
	def homeURL(self, value):
		self.__homeURL = self.__stringSetter(value)

	@downloadFolder.setter
	def downloadFolder(self, value):
		assert os.path.isdir(os.path.abspath(value)), "[GenericSelenium | downloadFolder.setter] The path must be a directory folder."
		self.__downloadFolder = os.path.abspath(value)
