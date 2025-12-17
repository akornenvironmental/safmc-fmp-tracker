/**
 * Development Login Script
 *
 * Generates a valid JWT token for local development without email magic links.
 * Usage: node dev-login.js <email>
 */

import jwt from 'jsonwebtoken';
import pg from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const { Pool } = pg;

// For local dev, don't use SSL. For production, use SSL.
const isLocalDB = process.env.DATABASE_URL && process.env.DATABASE_URL.includes('localhost');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: isLocalDB ? false : { rejectUnauthorized: false }
});

async function generateDevLogin(email) {
  try {
    // Find user by email
    const userResult = await pool.query(
      'SELECT id, name, email, role FROM users WHERE email = $1',
      [email]
    );

    if (userResult.rows.length === 0) {
      console.error(`❌ User not found: ${email}`);
      process.exit(1);
    }

    const user = userResult.rows[0];

    // Generate JWT token (must match server SECRET_KEY in .env)
    const token = jwt.sign(
      {
        user_id: user.id,  // Use snake_case to match Flask backend expectations
        email: user.email,
        name: user.name,
        role: user.role
      },
      process.env.SECRET_KEY || 'dev-secret-key-change-in-production',
      { expiresIn: '7d' }
    );

    console.log('\n✅ Development Login Token Generated!\n');
    console.log('User:', user.name);
    console.log('Email:', user.email);
    console.log('Role:', user.role);
    console.log('\n🔑 JWT Token:');
    console.log(token);
    console.log('\n📋 To use this token, paste this into your browser console:\n');
    console.log(`localStorage.setItem('authToken', '${token}');\nwindow.location.href = '/';\n`);
    console.log('\n🌐 Or visit this URL:\n');
    console.log(`http://localhost:5174/dev-login?token=${encodeURIComponent(token)}\n`);

    await pool.end();
  } catch (error) {
    console.error('❌ Error generating dev login:', error);
    process.exit(1);
  }
}

const email = process.argv[2];
if (!email) {
  console.error('Usage: node dev-login.js <email>');
  process.exit(1);
}

generateDevLogin(email);
