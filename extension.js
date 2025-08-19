const vscode = require('vscode');
const { Octokit } = require("octokit");
const fs = require('fs');
const { mkdir } = require('node:fs');
const { join } = require('node:path');
const path = require('path');
const { spawn, execSync } = require('child_process');
let developerId = '';
let busy = false;
let isConnected = false;
let file_name_w_ext, assertions_file, assertions_folder, uri, relevantFile, codePatch;
let remoteURL= '';
const simpleGit = require('simple-git/promise');

async function findFilePath(){
    const editor = vscode.window.activeTextEditor;
    uri = editor.document.uri.fsPath;
    const dir = path.dirname(uri);
    file_name_w_ext = path.basename(uri);
    const file_name_wo_ext = path.parse(file_name_w_ext).name;
    assertions_folder = join(dir, 'GAIB', 'assertions');
    assertions_file = join(assertions_folder, file_name_wo_ext + '.txt');
}

// Function to retrieve the path to the Python interpreter
function getPythonPath() {
    return new Promise((resolve, reject) => {
        const pythonScript = 'import sys; print(sys.executable)';
        const pythonProcess = spawn('python', ['-c', pythonScript]);

        pythonProcess.stdout.on('data', (data) => {
            const pythonPath = data.toString().trim();
            resolve(pythonPath);
        });

        pythonProcess.stderr.on('data', (data) => {
            reject(`Error retrieving Python path: ${data}`);
        });
    });
}

// Function to authenticate user
async function authenticate(username, password) {
    busy = true
    const pythonPath = await getPythonPath();
    const authScript = path.resolve(__dirname, 'scripts', 'authenticate.py');

    //vscode.window.showInformationMessage("Generating new assertions...")
    const pythonProcess = spawn(pythonPath, [authScript, username, password]);

    pythonProcess.stdout.on('data', (data) => {
        const result = data.toString().trim();
        console.log(result);
        if (result.includes("Error: ")) {
            vscode.window.showErrorMessage(result)
        } else {
            vscode.window.showInformationMessage("Successfully logged in")
            developerId = result
        }
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Error executing Python script: ${data}`);
        vscode.window.showErrorMessage(`Error executing Python script: ${data}`)
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python script exited with code ${code}`);
        busy = false
    });
}

// Function to create or edit assertions
async function editAssertions() {
    try {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.languageId !== 'python') {
            vscode.window.showErrorMessage('Please open a Python file to edit assertions.');
            return;
        }
        if (busy) {
            vscode.window.showErrorMessage('GAIB is already working on something. Please wait and try again.');
            return;
        }

        findFilePath();

        await mkdir(assertions_folder, {recursive: true}, (err) => {
            if (err) throw err;
        });
        
        
            if (!fs.existsSync(assertions_file)) {
                let fileCreate = fs.createWriteStream(assertions_file);
                fileCreate.close();
            }
        
        
            vscode.window.showTextDocument(vscode.Uri.file(assertions_file), {
                viewColumn: -2
                
            });
            vscode.window.showInformationMessage("Don't forget to save your assertions!")
    } catch (error) {
        console.error('Error editing assertions:', error);
        vscode.window.showErrorMessage('Error editing assertions. See console for details.');
    }
}

async function generateAssertions() {
    try {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.languageId !== 'python') {
            vscode.window.showErrorMessage('Please open a Python file to generate assertions.');
            return;
        }
        if (developerId == '') {
            vscode.window.showErrorMessage('You must log in before generating assertions.');
            return;
        }

        findFilePath();
        
        if (!fs.existsSync(assertions_file)) {
            vscode.window.showErrorMessage("No assertions found for current file. Use command 'GAIB: Edit Assertions' to create assertions.");
            return;
        }
        if (busy) {
            vscode.window.showErrorMessage('GAIB is already working on something. Please wait and try again.');
            return;
        }

        busy = true;
        
        const pythonPath = await getPythonPath();
        const generateTestScriptPath = path.resolve(__dirname, 'scripts', 'GenerateTests.py');
        
        vscode.window.showInformationMessage("Generating new assertions. Please wait...")
        const pythonProcess = spawn(pythonPath, [generateTestScriptPath, uri, assertions_file, developerId]);

        pythonProcess.stdout.on('data', (data) => {
            const result = data.toString().trim();
            console.log(result)
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`Error executing Python script: ${data}`);
            vscode.window.showErrorMessage("Error generating assertions. Please ensure you manually create three assertions before automatically generating assertions.")
        });

        pythonProcess.on('close', (code) => {
            busy = false
            console.log(`Python script exited with code ${code}`);
            if (code == 0) { vscode.window.showInformationMessage("Generated new assertions. Run command 'GAIB: Edit Assertions' to check and verify them, then run 'GAIB: Run Tests'.")}
        });
        
        
        
    } catch (error) {
        console.error('Error generating assertions:', error);
        vscode.window.showErrorMessage('Error generating assertions. Please ensure you manually create three assertions before automatically generating assertions.');
        busy = false
    }
}

// Function to run tests on the code
async function runTests() {
    try {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.languageId !== 'python') {
            vscode.window.showErrorMessage('Please open a Python file to run tests.');
            return;
        }
        if (developerId == '') {
            vscode.window.showErrorMessage('You must log in before running tests.');
            return;
        }

        findFilePath();

        if (!fs.existsSync(assertions_file)) {
            vscode.window.showErrorMessage("No assertions found for current file. Use command 'GAIB: Edit Assertions' to create assertions.");
            return;
        }
        if (busy) {
            vscode.window.showErrorMessage('GAIB is already working on something. Please wait and try again.');
            return;
        }
        busy = true;

        const pythonPath = await getPythonPath();
        const runTestsScriptPath = path.resolve(__dirname, 'scripts', 'RunTests.py');

        const pythonProcess = spawn(pythonPath, [runTestsScriptPath, uri, assertions_file, developerId]);
        vscode.window.showInformationMessage("Running tests. Please wait...");

        pythonProcess.stdout.on('data', (data) => {
            const result = data.toString().trim();
            console.log(result)
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`Error executing Python script: ${data}`);
            vscode.window.showErrorMessage("There was an error running tests. Check the console for details.")
        });

        pythonProcess.on('close', (code) => {
            busy = false;
            console.log(`Python script exited with code ${code}`);
            if (code == 0) {
                vscode.window.showInformationMessage("Ran tests.");
            }
        });

        
        
    } catch (error) {
        console.error('Error running tests:', error);
        vscode.window.showErrorMessage('Error running tests. See console for details.');
        busy = false;
    }
}

async function viewReport() {
    if (developerId == '') {
        vscode.window.showErrorMessage('You must log in before viewing report.');
        return;
    }

    vscode.env.openExternal(vscode.Uri.parse('http://130.113.68.57:3000/main/' + developerId));
}


async function updateAssertions(){
    findFilePath();
    const pythonPath = await getPythonPath();
    const updateTestScriptPath = path.resolve(__dirname, 'scripts', 'UpdateTests.py');
    
    await diffParser();

    vscode.window.showInformationMessage("Updating assertions. Please wait...")
    console.log(codePatch)
    const pythonProcess = spawn(pythonPath, [updateTestScriptPath, uri, assertions_file, codePatch, developerId]);

    pythonProcess.stdout.on('data', (data) => {
        const result = data.toString().trim();
        console.log(result)
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Error executing Python script: ${data}`);
        vscode.window.showErrorMessage("Error updating assertions. See console for details.")
    });

    pythonProcess.on('close', (code) => {
        busy = false
        console.log(`Python script exited with code ${code}`);
        if (code == 0) { vscode.window.showInformationMessage("Updated assertions. Run command 'GAIB: Edit Assertions' to check and verify them, then run 'GAIB: Run Tests'.")}
    });
}

async function githubLink(){
    const git = simpleGit(vscode.workspace.rootPath); // Initialize simple-git with the workspace root path
    const remotes = await git.getRemotes(true);
    if (!remotes){
        console.log("wrong");
        return false;
    }
    else{
        const githubRemote = remotes.find(remote => remote.name === 'origin' && remote.refs.fetch.includes('github.com'));
        if (githubRemote) {
            const urlParts = githubRemote.refs.fetch.split('/');
            const owner = urlParts[urlParts.length - 2];
            const repo = urlParts[urlParts.length - 1].replace('.git', '');2
            remoteURL = `${owner}/${repo}`;
            console.log("remoteURL: ", remoteURL);
            vscode.window.showInformationMessage("GitHub Connected")
            return true;
        } 
        else {
            vscode.window.showWarningMessage('GitHub repository not found or not connected.');
            console.error('GitHub remote not found');
            return false;
        }
    }
    
}

async function diffParser(){
    const octokit = new Octokit();
    try{

        findFilePath();

        //const isConnected = await githubLink();
        if (!isConnected){
            console.log('GitHub connection not established. Skipping Diff Parser.');
            return;
        }
        
        try {
            const { data: repoInfo } = await octokit.rest.repos.get({ owner: remoteURL.split('/')[0], repo: remoteURL.split('/')[1] });
            if (repoInfo.private) {
                vscode.window.showWarningMessage('Connected GitHub repository is private.');
                return;
            }
        } catch (error) {
            console.error('Error fetching repository information:', error);
            vscode.window.showErrorMessage('Error fetching repository information. Please check your GitHub connection.');
            return;
        }

        async function fetchCommitInfo() {
            try {
                const url = `GET /repos/${remoteURL}/commits/HEAD`;
                console.log("Fetching commit information from:", url); // Log the URL being fetched
                // Get the latest commit for the repository
                const { data: commit } = await octokit.request(url);
                //console.log(JSON.stringify(commit, null, 2)); // Log the whole commit information
                processCommitInfo(commit);
            } catch (error) {
                console.error('Error fetching commit information:', error);
                vscode.window.showErrorMessage('Error fetching commit information.');
            }
        }

        async function fetchFileContent(url) {
            try {
                const response = await octokit.request('GET ' + url);
                return response.data; // Return the content of the file
            } catch (error) {
                console.error('Error fetching file content:', error);
                vscode.window.showErrorMessage('Error fetching file content.');
                return '';
            }
        }

        async function processCommitInfo(commit) {
            try {
                if (!commit) {
                    vscode.window.showWarningMessage('Ensure a public GitHub repository is linked.');
                } else {
                    const files = commit.files || [];
                    relevantFile = files.find(file => file.filename === file_name_w_ext && (file.status === 'added' || file.status === 'modified'));
                    if (relevantFile) {
                        const fileContent = await fetchFileContent(relevantFile.raw_url);
                        //console.log(`File: ${relevantFile.filename}`);
                        //console.log(`Changes: ${relevantFile.patch}`);
                        codePatch = relevantFile.patch;
                    } else {
                        console.log(`File ${file_name_w_ext} not found or not modified in this commit.`);
                    }
                }
            } catch (error) {
                console.error('Error processing commit:', error);
                vscode.window.showErrorMessage('Error processing commit.');
            }
        }
        await fetchCommitInfo();
        // generateDiffAssertions();
        vscode.workspace.onDidChangeWorkspaceFolders(async () => {
            await fetchCommitInfo();
        });
    }
    catch (error){
        console.error('Error:', error);
        vscode.window.showErrorMessage('Error occurred. Please check the console for details.');
    }

}

async function install_libraries() {
    const pythonPath = await getPythonPath();

    // werkzeug
    try {
        execSync(pythonPath + ' -m pip show werkzeug');
        console.log("Already have library werkzeug.");
    } catch (error) {
        execSync(pythonPath + ' -m pip install werkzeug --user');
        console.log("Installed library werkzeug.");
    }
    // pymongo
    try {
        execSync(pythonPath + ' -m pip show pymongo');
        console.log("Already have library pymongo.");
    } catch (error) {
        execSync(pythonPath + ' -m pip install pymongo --user');
        console.log("Installed library pymongo.");
    }
    // pathlib
    try {
        execSync(pythonPath + ' -m pip show pathlib');
        console.log("Already have library pathlib.");
    } catch (error) {
        execSync(pythonPath + ' -m pip install pathlib --user');
        console.log("Installed library pathlib.");
    }
    // openai
    try {
        execSync(pythonPath + ' -m pip show openai');
        console.log("Already have library openai.");
    } catch (error) {
        execSync(pythonPath + ' -m pip install openai --user');
        console.log("Installed library openai.");
    }
    // pylint
    try {
        execSync(pythonPath + ' -m pip show pylint');
        console.log("Already have library pylint.");
    } catch (error) {
        execSync(pythonPath + ' -m pip install pylint --user');
        console.log("Installed library pylint.");
    }
    // pytest
    try {
        execSync(pythonPath + ' -m pip show pytest');
        console.log("Already have library pytest.");
    } catch (error) {
        execSync(pythonPath + ' -m pip install pytest --user');
        console.log("Installed library pytest.");
    }
    // coverage
    try {
        execSync(pythonPath + ' -m pip show coverage');
        console.log("Already have library coverage.");
    } catch (error) {
        execSync(pythonPath + ' -m pip install coverage --user');
        console.log("Installed library coverage.");
    }
}

// Activate function
async function activate(context) {

    await install_libraries();
    vscode.window.showInformationMessage('GAIB successfully activated. Run command "GAIB: Login" to get started.')

    // Command to login
    let loginDisposable = vscode.commands.registerCommand('genai.login', async () => {
        const username = await vscode.window.showInputBox({ prompt: 'Enter your username' });
        const password = await vscode.window.showInputBox({ prompt: 'Enter your password', password: true });
        if (!username || !password) return;
        await authenticate(username, password);
    });
    context.subscriptions.push(loginDisposable);

    let diffDisposable = vscode.commands.registerCommand('genai.diffParser', async () => {
        try {
            // await githubLink();
            await diffParser();
        } catch (error){
            console.error('Diff Parser cannot connect', error);
        }
    });
    context.subscriptions.push(diffDisposable);
    // Command to register
    /*let registerDisposable = vscode.commands.registerCommand('genai.register', async () => {
        const username = await vscode.window.showInputBox({ prompt: 'Enter your username' });
        const password = await vscode.window.showInputBox({ prompt: 'Enter your password', password: true });
        if (!username || !password) return;
        const success = await register(username, password);
        if (success) vscode.window.showInformationMessage('User registered successfully.');
        else vscode.window.showErrorMessage('Error registering user. Please try again.');
    });
    context.subscriptions.push(registerDisposable);*/
    
    let runTestsDisposable = vscode.commands.registerCommand('genai.runTests', async () => {
        await runTests();
    });
    context.subscriptions.push(runTestsDisposable);

    let editAssertionsDisposable = vscode.commands.registerCommand('genai.editAssertions', async () => {
        await editAssertions();
    });
    context.subscriptions.push(editAssertionsDisposable);

    let generateAssertionsDisposable = vscode.commands.registerCommand('genai.generateAssertions', async () => {
        await generateAssertions();
    });
    context.subscriptions.push(generateAssertionsDisposable);

    let viewReportDisposable = vscode.commands.registerCommand('genai.viewReport', async () => {
        await viewReport();
    });
    context.subscriptions.push(viewReportDisposable)

    let connectGitDisposable = vscode.commands.registerCommand('genai.connectGit', async () => {
        isConnected = await githubLink();
    });
    context.subscriptions.push(connectGitDisposable);

    let updateAssertionsDisposable = vscode.commands.registerCommand('genai.updateAssertions', async () => {
        await updateAssertions();
    })
}

exports.activate = activate;