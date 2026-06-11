import type { Handle } from '@sveltejs/kit';

// No-op for now. If we ever need to mutate every request (e.g., add a request ID
// header for tracing), it goes here.
export const handle: Handle = async ({ event, resolve }) => {
    return resolve(event);
};
