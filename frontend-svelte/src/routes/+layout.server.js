// Layout server-side error handling
export function load({ url, locals }) {
  return {
    url: url.pathname,
    apiKey: locals.apiKey
  };
}