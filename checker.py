import sys
import os
import subprocess

myPath = os.path.abspath('') + "\\CodeJudge\\"

class Compiler:

	"""docstring for compiler"""
	def __init__(self, lang, prbN):
            self.lang = lang
            self.prbN = prbN
            self.runTime = 0
            self.errorCompilation = False
            self.errorTLE = False
            self.errorRTE = False
            self.errorWA = False

            self.error = False
            self.error_text = "None"
            self.compile_percentage = 0

	def compile(self, filelocation, filename):

            """
            if self.lang == "java":
                filePath = myPath + "processServer\\batch\\"+self.batch_file_name+" "+path_+" "+filename+" "+filename.split(".")[0] + " " + myPath + "processServer\\batch\\" + " " + "p"+self.prbN
            elif self.lang == "py":
                filePath = myPath + "processServer\\batch\\"+self.batch_file_name+" "+path_+" "+filename+" " + myPath + "processServer\\batch\\" + " " + "p"+self.prbN
            elif self.lang == "cpp":
                filePath = myPath + "processServer\\batch\\"+self.batch_file_name+" "+path_+" "+filename+" " + myPath + "processServer\\batch\\" + " " + "p"+self.prbN
            """
            if self.lang == "java":
                invokerCmd = myPath + "static\\batch\\java.bat" + " " + myPath + " " + filelocation + " " + "p" + self.prbN + " " + filename + " " + filename.split(".")[0]
                self.runTime = 5
            if self.lang == "cpp":
                invokerCmd = myPath + "static\\batch\\cpp.bat" + " " + myPath + " " + filelocation + " " + "p" + self.prbN + " " + filename
                self.runTime = 3
            if self.lang == "py":
                invokerCmd = myPath + "static\\batch\\py.bat" + " " + myPath + " " + filelocation + " " + "p" + self.prbN + " " + filename
                self.runTime = 5

            p = subprocess.Popen( invokerCmd, stdout = subprocess.PIPE )
            try:
                stdout,stderr = p.communicate(timeout = self.runTime)

            except subprocess.TimeoutExpired:
                #p.kill()
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(p.pid)])
                stdout = "#TimeLimitExceded"
            self.error_text = str(stdout)
            return str(self.error_text)
	
	def getLastError(self):
            return self.error_text


def submitAnswer(file_name, uid, prbN, lang, file_path):

	fileLocation = myPath + "data\\users\\" + uid + "\\" + prbN

	if not os.path.exists(fileLocation):
		os.makedirs( fileLocation)
    
    #copying
	h = open( fileLocation + "\\" + file_name + "." + lang, 'w')
	f = open(file_path, 'r')
	h.write(f.read())
	h.close()
	f.close()
	
	compiler = Compiler(lang, prbN)

	score = compiler.compile( fileLocation, file_name + "." + lang)
	
	return score

def main():
	
	s_ = submitAnswer(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
	print(s_)


if __name__ == "__main__":
	main()