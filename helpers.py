import os

# Clean a string with lines starting with #
def cleanComments(input_string):
    lines = input_string.split('\n')
    lines_without_comments = [line for line in lines if not line.startswith('#')]
    output_string = '\n'.join(lines_without_comments)
    return output_string

# Clean a string from empty lines
def cleanEmptyLines(input_string):
    lines = input_string.split('\n')
    lines_without_empties = [line for line in lines if not line == ""]
    output_string = '\n'.join(lines_without_empties)
    return output_string

# Clean a string from empty lines and comments
def cleanCommentsAndLines(input_string):
    input_string = cleanComments(input_string)
    input_string = cleanEmptyLines(input_string)
    return input_string

#Cleans the output path and ensures it has a slash at the end.
def addSlash(output_path):
    if not output_path.endswith("/"):
        output_path += "/"
    return output_path

# Creates a directory if it does not exist
def createOutDir(outputPath):
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

# Extract filename from string url
def extractFileName(channelId, url):
    #Remove get data from url
    getDataIndex = url.rfind("?")
    if getDataIndex != -1:
        url = url[:getDataIndex]
    #Leave only last 6 slash and replace them with _
    if "smil:" in url:
        url = url[url.rfind("/")+1:]
    else:
        url = url.split("/")[-6:]
        url = "_".join(url)
    return channelId + "_" + url

# Remove the extension from a file name
def removeExtension(file_name):
    last_dot_index = file_name.rfind(".")
    base_name = file_name[:last_dot_index]
    return base_name

# Remove the extension from a file name
def getExtension(file_name):
    last_dot_index = file_name.rfind(".")
    extension = file_name[last_dot_index:]
    return extension

# Class for outputting and managing errors 
class Error:
    def __init__(self):
        self.errorLocation = "Unavailable"
        self.msg = "No Message"
        self.errorFatal = False

    def report(self, msg = "", errorLocation = "", fatal = False):
        self.errorLocation = errorLocation
        self.msg = msg
        self.errorFatal = fatal
        self.logError()

    def logError(self):
        print("Error found in " + self.errorLocation + ": " + self.msg)
        if self.errorFatal:
            print("Error is fatal. Exiting")
            exit()

    def hasError(self):
        if self.errorExist == True:
            self.logError
