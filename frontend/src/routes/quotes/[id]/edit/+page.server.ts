import { callBackend } from '$lib/api';
import type { BcQuoteLine, BcSalesQuote } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
    const quoteNo = event.params.id;
    const [headerRes, linesRes] = await Promise.all([
        callBackend<BcSalesQuote>(
            event,
            `/api/bc/sales-quotes/${encodeURIComponent(quoteNo)}/header`
        ),
        callBackend<BcQuoteLine[]>(
            event,
            `/api/bc/sales-quotes/${encodeURIComponent(quoteNo)}/lines`
        )
    ]);
    return {
        quoteNo,
        quote: headerRes.data ?? null,
        lines: linesRes.data ?? [],
        error: headerRes.error || linesRes.error
    };
};
