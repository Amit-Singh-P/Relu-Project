const axios = require('axios');
const { ENRICHMENT_JSON_SCHEMA, EMPTY_ENRICHMENT_PROFILE } = require('../config/aiConfig');

/**
 * Builds the instruction prompt sent to the AI provider.
 */
const buildPrompt = (websiteName, url) => {
  return `You are a company research assistant. Research the company below using the
information you know and reasonable inference. Respond with ONLY a valid JSON object
that strictly matches this schema (same field names, same structure, no extra fields,
no markdown, no commentary). If you do not know a value, use null instead of guessing.

Schema fields:
${JSON.stringify(ENRICHMENT_JSON_SCHEMA.properties, null, 2)}

Company Website Name: ${websiteName}
Company URL: ${url}`;
};

/**
 * Attempts to parse a JSON object out of raw AI text output, tolerating
 * accidental markdown code fences.
 */
const parseAIResponse = (rawText) => {
  if (!rawText || typeof rawText !== 'string') {
    throw new Error('Empty response received from AI provider.');
  }

  let cleaned = rawText.trim();
  cleaned = cleaned.replace(/^```json/i, '').replace(/^```/, '').replace(/```$/, '').trim();

  const firstBrace = cleaned.indexOf('{');
  const lastBrace = cleaned.lastIndexOf('}');
  if (firstBrace === -1 || lastBrace === -1) {
    throw new Error('AI provider did not return a valid JSON object.');
  }

  const jsonSlice = cleaned.slice(firstBrace, lastBrace + 1);

  try {
    return JSON.parse(jsonSlice);
  } catch (err) {
    throw new Error('Failed to parse JSON returned by AI provider.');
  }
};

/**
 * Merges the AI's parsed output onto the empty schema shape so every
 * expected field is always present in the saved profile.
 */
const normalizeProfile = (parsed) => {
  return {
    ...EMPTY_ENRICHMENT_PROFILE,
    ...parsed,
    socialLinks: {
      ...EMPTY_ENRICHMENT_PROFILE.socialLinks,
      ...(parsed.socialLinks || {})
    }
  };
};

const callOpenAI = async (prompt, apiKey, model) => {
  const response = await axios.post(
    'https://api.openai.com/v1/chat/completions',
    {
      model: model || 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'You only respond with valid JSON. No prose, no markdown.' },
        { role: 'user', content: prompt }
      ],
      temperature: 0.2
    },
    {
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    }
  );

  return response.data.choices[0].message.content;
};

const callGemini = async (prompt, apiKey, model) => {
  const modelName = model || 'gemini-1.5-flash';
  const response = await axios.post(
    `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${apiKey}`,
    {
      contents: [
        {
          parts: [{ text: prompt }]
        }
      ],
      generationConfig: {
        temperature: 0.2
      }
    },
    {
      headers: { 'Content-Type': 'application/json' }
    }
  );

  return response.data.candidates[0].content.parts[0].text;
};

const callClaude = async (prompt, apiKey, model) => {
  const response = await axios.post(
    'https://api.anthropic.com/v1/messages',
    {
      model: model || 'claude-3-5-sonnet-20241022',
      max_tokens: 1024,
      messages: [{ role: 'user', content: prompt }]
    },
    {
      headers: {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'Content-Type': 'application/json'
      }
    }
  );

  return response.data.content[0].text;
};

/**
 * Calls the AI provider configured via environment variables and returns
 * a normalized enrichment profile object matching ENRICHMENT_JSON_SCHEMA.
 */
const enrichCompany = async (websiteName, url) => {
  const provider = (process.env.AI_PROVIDER || 'openai').toLowerCase();
  const apiKey = process.env.AI_API_KEY;
  const model = process.env.AI_MODEL;

  if (!apiKey) {
    const err = new Error('AI_API_KEY is not configured on the server.');
    err.statusCode = 500;
    throw err;
  }

  const prompt = buildPrompt(websiteName, url);
  let rawText;

  try {
    if (provider === 'openai') {
      rawText = await callOpenAI(prompt, apiKey, model);
    } else if (provider === 'gemini') {
      rawText = await callGemini(prompt, apiKey, model);
    } else if (provider === 'claude') {
      rawText = await callClaude(prompt, apiKey, model);
    } else {
      const err = new Error(`Unsupported AI_PROVIDER "${provider}". Use openai, gemini, or claude.`);
      err.statusCode = 500;
      throw err;
    }
  } catch (error) {
    if (error.response) {
      const err = new Error(
        `AI provider request failed: ${error.response.status} ${JSON.stringify(error.response.data)}`
      );
      err.statusCode = 502;
      throw err;
    }
    throw error;
  }

  const parsed = parseAIResponse(rawText);
  return normalizeProfile(parsed);
};

module.exports = { enrichCompany };
