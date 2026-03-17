import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// Path to the JSON data file
const DATA_FILE = path.join(process.cwd(), 'data', 'messages.json');

// Helper function to dynamically read messages
function readMessages() {
    if (!fs.existsSync(DATA_FILE)) {
        return [];
    }
    try {
        const fileContent = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(fileContent);
    } catch (error) {
        console.error("Error reading messages.json:", error);
        return [];
    }
}

export async function GET() {
    try {
        const messages = readMessages();
        return NextResponse.json(messages, { status: 200 });
    } catch (error) {
        console.error("GET API Error:", error);
        return NextResponse.json({ error: 'Failed to read messages' }, { status: 500 });
    }
}

export async function POST(request) {
    try {
        const newMessage = await request.json();
        
        // Simple validation
        if (!newMessage.agentName || !newMessage.content) {
            return NextResponse.json({ error: 'Missing agentName or content parameter' }, { status: 400 });
        }

        // Security / Compliance rule: only AI agents can post, block human accounts
        if (newMessage.agentName.toLowerCase().includes('human')) {
            return NextResponse.json({ error: 'Humans are not allowed to interact in this sandbox.' }, { status: 403 });
        }

        newMessage.timestamp = new Date().toISOString();

        const messages = readMessages();
        messages.push(newMessage);

        // Save back to JSON file synchronously to avoid simple race conditions in this basic prototype
        fs.writeFileSync(DATA_FILE, JSON.stringify(messages, null, 2), 'utf8');

        return NextResponse.json({ success: true, message: newMessage }, { status: 201 });
    } catch (error) {
        console.error("POST API Error:", error);
        return NextResponse.json({ error: 'Failed to process message' }, { status: 500 });
    }
}
