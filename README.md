# -Supply-Chain-Blockchain-Tracker
A command-line application that simulates a blockchain-based supply chain tracking system built entirely from scratch in Python. Track products across their entire journey — from dispatch to delivery — with cryptographic integrity and role-based access control.
This project demonstrates how blockchain technology can be applied to supply chain management. Every supply chain event (dispatch, transit, delivery) is stored as a block in a tamper-proof chain. If any block is modified, the chain validation immediately detects it.
Features:-
⛓️ Blockchain from Scratch — Block creation, SHA-256 hashing, Proof-of-Work mining
🔒 Tamper Detection — Chain validation detects any modification to historical blocks
👤 Role-Based Access Control — Separate admin and user roles with different permissions
🔑 Secure Authentication — Passwords hashed with SHA-256 before storage
💾 Persistent Storage — Blockchain and user data saved as JSON files across sessions
🔍 Search & Filter — Search events by Product ID or by username
🖥️ Color-Coded CLI — Clean, readable terminal interface using Colorama
📊 Tabular Display — Formatted tables using Tabulate for easy data viewing
