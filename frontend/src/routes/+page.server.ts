import { callBackend } from '$lib/api';
import type { BcCustomer, BcSalesOrder, BcSalesQuote, IntegrationStatus } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
    // Pull live BC data in parallel: customers, all quotes (filtered client-side
    // because statuses are Draft|Open|Released), open orders, integration status.
    const [customersRes, quotesRes, ordersRes, intRes] = await Promise.all([
        callBackend<BcCustomer[]>(event, '/api/bc/customers?top=2000'),
        callBackend<BcSalesQuote[]>(event, '/api/bc/sales-quotes?top=200'),
        callBackend<BcSalesOrder[]>(event, '/api/bc/sales-orders?status=Open&top=200'),
        callBackend<IntegrationStatus>(event, '/api/integrations')
    ]);

    return {
        customers: customersRes.data ?? [],
        quotes: quotesRes.data ?? [],
        orders: ordersRes.data ?? [],
        integrations: intRes.data
    };
};
