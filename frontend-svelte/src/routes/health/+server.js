import { json } from '@sveltejs/kit';

/** @type {import('./$types').RequestHandler} */
export function GET() {
  return json({ status: 'ok', timestamp: new Date().toISOString() });
}