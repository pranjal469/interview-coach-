import json

questions = {
    "software_engineer": {
        "behavioral": [
            "Tell me about a time you disagreed with a teammate's technical decision. How did you handle it?",
            "Describe a project where you had to learn a new technology quickly.",
            "Tell me about a time you missed a deadline. What happened?",
            "Describe a situation where you had to debug a difficult problem under pressure.",
            "Tell me about a time you received critical feedback on your code."
        ],
        "technical": [
            "How would you design a URL shortening service?",
            "Explain the difference between SQL and NoSQL databases, and when you'd use each.",
            "What is the time complexity of searching in a balanced binary search tree, and why?",
            "How would you handle a memory leak in a long-running application?",
            "Explain how you would test a REST API endpoint."
        ]
    },
    "data_analyst": {
        "behavioral": [
            "Tell me about a time your data analysis led to a business decision.",
            "Describe a situation where your initial analysis was wrong. How did you catch it?",
            "Tell me about a time you had to explain a complex finding to a non-technical stakeholder.",
            "Describe how you prioritize when given multiple analysis requests at once.",
            "Tell me about a time you worked with messy or incomplete data."
        ],
        "technical": [
            "How would you identify outliers in a dataset?",
            "Explain the difference between correlation and causation with an example.",
            "How would you handle missing data in a dataset before analysis?",
            "What SQL query would you write to find the second-highest value in a column?",
            "How would you design an A/B test to measure a new feature's impact?"
        ]
    },
    "product_manager": {
        "behavioral": [
            "Tell me about a time you had to say no to a feature request from a stakeholder.",
            "Describe a product decision you made that didn't work out as planned.",
            "Tell me about a time you had to align engineering and design teams with conflicting priorities.",
            "Describe how you handled a situation where a launch date was at risk.",
            "Tell me about a time you used user feedback to change a product direction."
        ],
        "technical": [
            "How would you prioritize a product roadmap with limited engineering resources?",
            "Walk me through how you would define success metrics for a new feature.",
            "How would you approach designing an onboarding flow for a new app?",
            "Explain how you would decide between building a feature in-house versus buying a solution.",
            "How would you estimate the market size for a new product idea?"
        ]
    },
    "marketing": {
        "behavioral": [
            "Tell me about a campaign that underperformed. What did you learn?",
            "Describe a time you had to work with a very limited budget.",
            "Tell me about a time you used data to change a marketing strategy.",
            "Describe how you handled disagreement with a creative team on messaging.",
            "Tell me about a campaign you're most proud of and why."
        ],
        "technical": [
            "How would you measure the ROI of a social media campaign?",
            "Walk me through how you would plan a product launch campaign.",
            "How would you approach segmenting an email list for better engagement?",
            "Explain how you would choose between paid and organic growth channels.",
            "How would you A/B test a landing page for conversion rate?"
        ]
    },
    "hr_recruiter": {
        "behavioral": [
            "Tell me about a time you had to reject a strong candidate. How did you communicate it?",
            "Describe a situation where you had to fill a role with a very tight deadline.",
            "Tell me about a time a hiring manager disagreed with your recommendation.",
            "Describe how you handled a difficult conversation with an employee.",
            "Tell me about a time you improved a hiring process."
        ],
        "technical": [
            "How would you evaluate a candidate's culture fit without bias?",
            "Walk me through how you would source candidates for a hard-to-fill role.",
            "How would you design a fair and structured interview process?",
            "Explain how you would measure the success of a recruitment campaign.",
            "How would you handle a high volume of applications for one role?"
        ]
    }
}

with open("questions.json", "w") as f:
    json.dump(questions, f, indent=2)

total = sum(len(v['behavioral']) + len(v['technical']) for v in questions.values())
print(f"Question bank saved with {total} questions across {len(questions)} roles")