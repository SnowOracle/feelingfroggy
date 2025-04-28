#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up GitHub repository for Feeling Froggy...${NC}"

# 1. Initialize Git repository if not already initialized
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Initializing Git repository...${NC}"
    git init
    echo -e "${GREEN}Git repository initialized!${NC}"
else
    echo -e "${YELLOW}Git repository already exists.${NC}"
fi

# 2. Create .gitignore file
echo -e "${YELLOW}Creating .gitignore file...${NC}"
cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Streamlit
.streamlit/secrets.toml

# Database
*.db
*.sqlite
*.sqlite3

# Files that might contain sensitive data
*secrets*
*credentials*

# macOS
.DS_Store
EOL
echo -e "${GREEN}.gitignore file created!${NC}"

# 3. Create a README.md file if it doesn't exist
if [ ! -f "README.md" ]; then
    echo -e "${YELLOW}Creating README.md file...${NC}"
    cat > README.md << EOL
# Feeling Froggy 🐸

An interactive Streamlit application for learning about frogs, their habitats, calls, and identification.

## Features

- Frog call explorer with audio samples
- Interactive quiz on frog sounds
- Fun facts about frogs and their vocalizations

## Installation

1. Clone this repository:
   \`\`\`
   git clone https://github.com/YOUR-USERNAME/feelingfroggy.git
   cd feelingfroggy
   \`\`\`

2. Create a virtual environment and install dependencies:
   \`\`\`
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
   pip install -r requirements.txt
   \`\`\`

3. Set up the database:
   \`\`\`
   python setup.py
   \`\`\`

4. Download frog call audio files:
   \`\`\`
   python download_frog_calls.py
   \`\`\`

## Running the Application

Start the Streamlit server:
\`\`\`
streamlit run app.py
\`\`\`

Open your browser to http://localhost:8501

## Deployment

This app is deployed using Streamlit Cloud. Visit [our website](https://your-website.com) to see it live.

## License

[Add license information here]
EOL
    echo -e "${GREEN}README.md file created!${NC}"
else
    echo -e "${YELLOW}README.md already exists.${NC}"
fi

# 4. Create Procfile for deployment (if using Heroku or similar)
echo -e "${YELLOW}Creating Procfile for deployment...${NC}"
cat > Procfile << EOL
web: streamlit run app.py
EOL
echo -e "${GREEN}Procfile created!${NC}"

# 5. Stage files for commit
echo -e "${YELLOW}Staging files for commit...${NC}"
git add .
echo -e "${GREEN}Files staged!${NC}"

# 6. Initial commit
echo -e "${YELLOW}Creating initial commit...${NC}"
git commit -m "Initial commit for Feeling Froggy Streamlit app"
echo -e "${GREEN}Changes committed!${NC}"

# 7. Check for GitHub CLI installation
if command -v gh &> /dev/null; then
    has_github_cli=true
    echo -e "${GREEN}GitHub CLI is installed.${NC}"
else
    has_github_cli=false
    echo -e "${RED}GitHub CLI is not installed.${NC}"
    echo -e "${YELLOW}=== GitHub CLI Installation Instructions ===${NC}"
    echo -e "macOS: brew install gh"
    echo -e "Windows: winget install --id GitHub.cli"
    echo -e "Linux: Follow instructions at https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    echo -e "More details: https://cli.github.com/manual/installation"
    echo -e "${YELLOW}=== Continuing with manual steps ===${NC}"
fi

# 8. Prompt for GitHub repository creation
echo -e "${YELLOW}Do you want to create a GitHub repository now? (y/n)${NC}"
read -p "" create_repo

if [ "$create_repo" = "y" ] || [ "$create_repo" = "Y" ]; then
    # Get GitHub username and repo name
    echo -e "${YELLOW}Enter your GitHub username:${NC}"
    read -p "" github_username
    
    echo -e "${YELLOW}Enter repository name (default: feelingfroggy):${NC}"
    read -p "" repo_name
    repo_name=${repo_name:-feelingfroggy}
    
    if [ "$has_github_cli" = true ]; then
        echo -e "${YELLOW}Using GitHub CLI to create repository...${NC}"
        
        # Check if already authenticated with GitHub CLI
        gh auth status &> /dev/null
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}Please authenticate with GitHub CLI:${NC}"
            gh auth login
        fi
        
        # Create repository
        echo -e "${YELLOW}Enter repository description (optional):${NC}"
        read -p "" repo_description
        
        if [ -z "$repo_description" ]; then
            gh repo create "$repo_name" --public
        else
            gh repo create "$repo_name" --public --description "$repo_description"
        fi
        
        # Add remote
        git remote add origin "https://github.com/$github_username/$repo_name.git"
        
        # Push to GitHub
        echo -e "${YELLOW}Pushing to GitHub...${NC}"
        git branch -M main
        git push -u origin main
        
        echo -e "${GREEN}Repository successfully created and code pushed to GitHub!${NC}"
        echo -e "${GREEN}Repository URL: https://github.com/$github_username/$repo_name${NC}"
    else
        echo -e "${YELLOW}=== MANUAL GITHUB REPOSITORY CREATION ===${NC}"
        echo -e "1. Go to https://github.com/new"
        echo -e "2. Enter '$repo_name' as Repository name"
        echo -e "3. Choose 'Public' visibility"
        echo -e "4. Click 'Create repository'"
        echo -e "5. Follow the instructions below to push your code to the new repository"
        echo -e "\n${YELLOW}=== COMMANDS TO PUSH TO GITHUB ===${NC}"
        echo -e "Run these commands after creating your repository on GitHub:"
        echo -e "${GREEN}git remote add origin https://github.com/$github_username/$repo_name.git${NC}"
        echo -e "${GREEN}git branch -M main${NC}"
        echo -e "${GREEN}git push -u origin main${NC}"
    fi
    
    # Instructions for Streamlit Cloud deployment
    echo -e "\n${YELLOW}=== NEXT STEPS FOR STREAMLIT CLOUD DEPLOYMENT ===${NC}"
    echo -e "1. Go to https://share.streamlit.io/ and sign in with your GitHub account"
    echo -e "2. Click 'New app' and select your repository ($repo_name)"
    echo -e "3. Choose the main branch and enter 'app.py' as the main file path"
    echo -e "4. Click 'Deploy!'"
    echo -e "5. Once deployed, go to settings to add your custom domain"
    
    echo -e "\n${YELLOW}=== SQUARESPACE DNS CONFIGURATION ===${NC}"
    echo -e "1. In your Squarespace account, go to Settings > Domains"
    echo -e "2. Select your domain and go to 'DNS Settings'"
    echo -e "3. Add a CNAME record pointing to your Streamlit app URL"
    echo -e "4. Follow Streamlit's documentation for configuring your custom domain:\n   https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/custom-domains"
else
    echo -e "${YELLOW}Skipping GitHub repository creation.${NC}"
    echo -e "${YELLOW}To create a repository later:${NC}"
    echo -e "1. Create a new repository at https://github.com/new"
    echo -e "2. Then connect your local repository using:"
    echo -e "   ${GREEN}git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git${NC}"
    echo -e "   ${GREEN}git branch -M main${NC}"
    echo -e "   ${GREEN}git push -u origin main${NC}"
fi

echo -e "\n${GREEN}Setup completed!${NC}"
echo -e "${YELLOW}Note: You can run this script again if you need to see the GitHub instructions or Streamlit deployment steps again.${NC}" 