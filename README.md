# GenAI Test Bot (GAIB) README

To try this extension, go to visual studio marketplace and search "GAIB genai". The top result will be the extension "genAI" by publisher GAIB.That being said, we have been having technical difficulties trying to run this extension on various machines. Keep in mind that you may not be able to run this extension at all. If you have questions about this, reach out to us. We are still working to resolve these issues.

GAIB runs mostly through your VS Code Workspace through the command palette, accessed through Ctrl + Shift + P, and typing in GAIB. The following are the commands you can run on GAIB to generate test cases for your code.
The ideal order of running these commands is the order they are listed in below. Registration for an account happens on our website linked here: http://130.113.68.57:3000/ .

NOTE: You must be on McMaster Wifi (or using the VPN) to access the Website or properly use the extension.

GAIB: Login -  allows users to log in on the extension.

GAIB: Edit Assertions - allows users to upload a few assertions as sample test cases and to confirm the new assertions given to them by GAIB.

GAIB: Generate Assertions - takes the assertions from the assertion file created by the previous command and uses that as well as your code to generate additional assertions. (You should run "GAIB: Edit Assertions" again to check the generated assertions)

GAIB: Run Tests - checks that the assertions run and provide the output wanted.

GAIB: View Report - analyses the test cases generated and creates a report, which is displayed on our wesbite, on test case accuracy, static rating and coverage rating. It also specifies the specific reasoning behind the static rating under the static report section, and lists the generated test cases and whether they pass or fail.

PLEASE NOTE:
GAIB does have some restrictions when running that you will need to keep in mind. He will generate test cases for only the file currently being viewed when the GAIB: Edit Assertions and GAIB: Generate Assertions commands are run. GAIB has a diff parser that will take in a linked GitHub repository and will monitor commits to pass a patch for your latest commit to the test case generator. GAIB's diff parser needs a public repository to be linked to do this though! You must be logged in to run commands so make sure not to skip that step! A simple tip to help smoothen this process is if you change any code and want to re-run the tests, just refresh the Main page of our website.

