export type UserRole = 'superadmin' | 'admin';

export type User = {
    id: number;
    username: string;
    displayName: string | null;
    isAdmin: boolean;
    role: UserRole;
};

export type Job = {
    id: number;
    jobNumber: string;
    title: string;
    customerName: string;
    status: 'draft' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
    sfOpportunityId: string | null;
    bcSalesOrderId: string | null;
    scheduledFor: string | null;
    completedAt: string | null;
    notes: string | null;
    createdAt: string;
    updatedAt: string;
};

export type Quote = {
    id: number;
    quoteNumber: string;
    customerName: string;
    status: 'draft' | 'sent' | 'accepted' | 'rejected' | 'expired';
    totalAmount: number | null;
    currency: string;
    bcSalesQuoteId: string | null;
    sfOpportunityId: string | null;
    jobId: number | null;
    validUntil: string | null;
    notes: string | null;
    createdAt: string;
    updatedAt: string;
};

export type InventoryItem = {
    id: number;
    bcItemId: string | null;
    itemNumber: string;
    displayName: string;
    baseUnitOfMeasure: string | null;
    unitPrice: number | null;
    inventoryOnHand: number | null;
    lastSyncedAt: string;
};

export type SyncLog = {
    id: number;
    integration: string;
    entity: string;
    status: 'started' | 'success' | 'failed';
    startedAt: string;
    completedAt: string | null;
    recordsSynced: number;
    errorMessage: string | null;
};

export type IntegrationStatus = {
    businessCentral: {
        configured: boolean;
        lastSync: SyncLog | null;
    };
    salesforce: {
        configured: boolean;
        lastSync: SyncLog | null;
    };
};

export type PingResult = {
    connected: boolean;
    reason?: string;
    message?: string;
    [key: string]: unknown;
};

export type BcCustomer = {
    id?: string;
    systemId?: string;
    number: string;
    displayName: string;
    phoneNumber?: string;
    email?: string;
    contactName?: string;
    addressLine1?: string;
    addressLine2?: string;
    city?: string;
    state?: string;
    country?: string;
    countryRegionCode?: string;
    postalCode?: string;
    currencyCode?: string;
    paymentTermsId?: string;
    paymentTermsCode?: string;
    customerPriceGroup?: string;
    salesperson?: string;
    salespersonCode?: string;
    custCategory?: string;
    businessType?: string;
    blocked?: string;
};

export type BcQuoteLine = {
    systemId: string;
    documentNumber: string;
    lineNo: number;
    lineType: string;
    itemNo: string;
    variantCode?: string;
    locationCode?: string;
    description?: string;
    description2?: string;
    quantity: number;
    qtyToAssembleToOrder: number;
    unitOfMeasureCode?: string;
    unitPrice?: number;
    lineDiscountPct?: number;
    amountExcludingTax?: number;
    amountIncludingTax?: number;
};

export type BcAssemblyLine = {
    systemId: string;
    documentType: string;
    documentNo: string;
    lineNo: number;
    lineType: string;
    itemNo: string;
    variantCode?: string;
    description?: string;
    locationCode?: string;
    quantity: number;
    quantityPer: number;
    unitOfMeasureCode?: string;
    unitCost?: number;
};

export type BcAtoBundle = {
    assemblyDocType: string;
    assemblyDocNo: string;
    lines: BcAssemblyLine[];
};

export type BcDimensionValue = {
    systemId?: string;
    dimensionCode: string;
    code: string;
    name: string;
    blocked?: boolean;
};

export type BcComponentPriceResponse = {
    priceGroup: string | null;
    currency: string | null;
    prices: Array<{
        itemNo: string;
        variantCode: string;
        unitPrice: number | null;
    }>;
};

export type BcPaymentTerm = {
    id?: string;
    code: string;
    displayName?: string;
    dueDateCalculation?: string;
};

export type BcLocation = {
    id?: string;
    code: string;
    displayName?: string;
};

export type BcCustomerTemplate = {
    systemId: string;
    code: string;
    description: string;
    customerPriceGroup?: string;
    customerPostingGroup?: string;
    genBusPostingGroup?: string;
    paymentTermsCode?: string;
    paymentMethodCode?: string;
    currencyCode?: string;
    countryRegionCode?: string;
    salespersonCode?: string;
};

export type BcSalesQuote = {
    id: string;
    number: string;
    documentDate: string;
    dueDate?: string;
    validUntilDate?: string;
    status: string;
    customerNumber: string;
    customerName?: string;
    shipToName?: string;
    salesperson?: string;
    totalAmountExcludingTax: number;
    totalAmountIncludingTax: number;
    totalTaxAmount?: number;
    currencyCode?: string;
    externalDocumentNumber?: string;
    shortcutDimension1Code?: string;
    lastModifiedDateTime?: string;
    createdBy?: string | null;
};

export type BcSalesOrder = {
    id: string;
    number: string;
    orderDate: string;
    postingDate?: string;
    requestedDeliveryDate?: string;
    promisedDeliveryDate?: string;
    status: string;
    customerNumber: string;
    customerName?: string;
    shipToName?: string;
    salesperson?: string;
    totalAmountExcludingTax: number;
    totalAmountIncludingTax: number;
    totalTaxAmount?: number;
    currencyCode?: string;
    externalDocumentNumber?: string;
    shortcutDimension1Code?: string;
    lastModifiedDateTime?: string;
};

export type BcSkuRow = {
    id: string | null;
    itemNo: string;
    itemDescription: string;
    variantCode: string;
    variantDescription: string;
    unitOfMeasure: string;
    locationCode: string;
    replenishmentSystem: string;
    inventory: number;
    qtyOnSalesOrder: number;
    qtyOnPurchOrder: number;
    reorderPoint: number;
};

export type BcItemListing = {
    id: string | null;
    number: string;
    displayName: string;
    baseUnitOfMeasure: string | null;
    variantCount: number | null;
};

export type CustomerPriceGroup = {
    code: string;
    description: string;
};

export type VariantPrice = {
    groupCode: string;
    groupDescription: string;
    unitPrice: number | null;
    currency: string;
};

export type VariantPricingRow = {
    itemNo: string;
    itemDescription: string;
    variantCode: string;
    variantDescription: string;
    locationCode: string;
    unitOfMeasure: string;
    inventory: number | null;
    qtyOnSalesOrder: number;
    prices: VariantPrice[];
};

export type VariantPricingResponse = {
    priceGroups: CustomerPriceGroup[];
    rows: VariantPricingRow[];
    locations: string[];
};

export type PricingMatrix = {
    item: {
        id: string | null;
        number: string;
        displayName: string;
        baseUnitOfMeasure: string | null;
    };
    priceGroups: CustomerPriceGroup[];
    variants: Array<{
        code: string;
        description: string;
        inventory: number | null;
        prices: VariantPrice[];
    }>;
};
