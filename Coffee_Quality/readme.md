Coffee Quality Explorer
An interactive Streamlit app exploring 1,300+ Arabica coffees professionally graded by the Coffee Quality Institute — filter by country and processing method, see score distributions, check if altitude affects quality, and compare flavor profiles.

Run locally
bash
pip install -r requirements.txt
streamlit run app.py

Then open the URL shown in the terminal (usually http://localhost:8501).

Deploy for free (Streamlit Community Cloud)
Push this folder to a new GitHub repository (see commands below).
Go to https://share.streamlit.io and sign in with GitHub.
Click "New app", pick your repo/branch, and set the main file to app.py.
Click Deploy. You'll get a public URL like https://your-app-name.streamlit.app.
Generate a QR code for that URL (see below) so people can scan it during your presentation.
Push to GitHub
bash
git init
git add .
git commit -m "Coffee Quality Explorer"
git branch -M main
git remote add origin https://github.com/<your-username>/coffee-quality-explorer.git
git push -u origin main
Data source

Coffee Quality Institute review data, via the jldbc/coffee-quality-database GitHub repo.