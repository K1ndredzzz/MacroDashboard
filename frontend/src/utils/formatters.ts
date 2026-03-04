import type { LatestSnapshot } from '../types/api';

type NumericInput = number | string | null | undefined;

const toNumber = (value: NumericInput): number | null => {
  if (value === null || value === undefined) return null;
  if (typeof value === 'number') return Number.isFinite(value) ? value : null;

  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : null;
};

const isJpyPair = (indicatorCode: string): boolean => indicatorCode.toUpperCase().includes('JPY');

const isFxCode = (indicatorCode: string): boolean => {
  const code = indicatorCode.toUpperCase();
  return ['USD', 'EUR', 'JPY', 'GBP', 'CNY'].some((token) => code.includes(token));
};

const isLaborCount = (indicatorCode: string, unit?: string | null): boolean => {
  const code = indicatorCode.toUpperCase();
  const normalizedUnit = (unit || '').toLowerCase();

  return code.includes('PAYEMS') || code.includes('NONFARM') || normalizedUnit.includes('thousand');
};

const isFixedIncomeIndicator = (indicatorCode: string): boolean => {
  const code = indicatorCode.toUpperCase();
  return (/^US\d+Y$/.test(code) || code.includes('FEDFUNDS') || code.endsWith('RATE') || code.includes('YIELD'));
};

const isPercentUnit = (unit?: string | null): boolean => (unit || '').includes('%');

export const formatIndex = (
  value: NumericInput,
  options: { minFractionDigits?: number; maxFractionDigits?: number } = {}
): string => {
  const numericValue = toNumber(value);
  if (numericValue === null) return '-';

  const formatter = new Intl.NumberFormat('en-US', {
    minimumFractionDigits: options.minFractionDigits ?? 0,
    maximumFractionDigits: options.maxFractionDigits ?? 2
  });

  return formatter.format(numericValue);
};

export const formatCurrency = (
  value: NumericInput,
  options: { indicatorCode?: string } = {}
): string => {
  const numericValue = toNumber(value);
  if (numericValue === null) return '-';

  const code = options.indicatorCode || '';
  const isJpy = isJpyPair(code);
  const maxFractionDigits = isJpy ? 3 : (Math.abs(numericValue) < 1 ? 5 : 4);
  const minFractionDigits = isJpy ? 2 : 4;

  const formatter = new Intl.NumberFormat('en-US', {
    minimumFractionDigits: minFractionDigits,
    maximumFractionDigits: maxFractionDigits
  });

  return formatter.format(numericValue);
};

export const formatLatestSnapshotValue = (indicator: LatestSnapshot): string => {
  if (isLaborCount(indicator.indicator_code, indicator.unit)) {
    return formatIndex(indicator.latest_value, { maxFractionDigits: 0 });
  }

  const category = indicator.category?.toLowerCase() || '';
  if (category === 'fx' || isFxCode(indicator.indicator_code)) {
    return formatCurrency(indicator.latest_value, { indicatorCode: indicator.indicator_code });
  }

  if (category === 'rates') {
    return formatIndex(indicator.latest_value, { maxFractionDigits: 3 });
  }

  if (category === 'commodity') {
    return formatIndex(indicator.latest_value, { maxFractionDigits: 2 });
  }

  return formatIndex(indicator.latest_value, { maxFractionDigits: 2 });
};

export interface SnapshotChangeDisplay {
  direction: 'up' | 'down' | 'flat';
  text: string;
}

export const formatLatestSnapshotChange = (indicator: LatestSnapshot): SnapshotChangeDisplay | null => {
  const deltaAbs = toNumber(indicator.delta_abs);
  const deltaPct = toNumber(indicator.delta_pct);

  if (deltaAbs === null && deltaPct === null) {
    return null;
  }

  if (isFixedIncomeIndicator(indicator.indicator_code) && deltaAbs !== null) {
    const changeBps = deltaAbs * 100;
    return {
      direction: changeBps > 0 ? 'up' : changeBps < 0 ? 'down' : 'flat',
      text: `${Math.abs(changeBps).toFixed(0)} bps`
    };
  }

  if (isPercentUnit(indicator.unit) && deltaAbs !== null) {
    return {
      direction: deltaAbs > 0 ? 'up' : deltaAbs < 0 ? 'down' : 'flat',
      text: `${Math.abs(deltaAbs).toFixed(2)}%`
    };
  }

  const relativeChange = deltaPct ?? deltaAbs;
  if (relativeChange === null) {
    return null;
  }

  return {
    direction: relativeChange > 0 ? 'up' : relativeChange < 0 ? 'down' : 'flat',
    text: `${Math.abs(relativeChange).toFixed(2)}%`
  };
};
