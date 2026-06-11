import { callBackend } from '$lib/api';
import type { BcQuoteLine, BcSalesQuote } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
    const quoteNo = event.params.id;
    // Find the quote by number (the id route param is the quote number from the listing)
    const [quotesRes, linesRes] = await Promise.all([
        callBackend<BcSalesQuote[]>(
            event,
            `/api/bc/sales-quotes?q=${encodeURIComponent(quoteNo)}&top=1`
        ),
        callBackend<BcQuoteLine[]>(
            event,
            `/api/bc/sales-quotes/${encodeURIComponent(quoteNo)}/lines`
        )
    ]);
    const quote = (quotesRes.data ?? []).find((q) => q.number === quoteNo) ?? null;
    return {
        quoteNo,
        quote,
        lines: linesRes.data ?? [],
        error: quotesRes.error || linesRes.error
    };
};
