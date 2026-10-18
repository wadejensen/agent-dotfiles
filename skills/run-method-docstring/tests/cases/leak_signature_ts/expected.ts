export interface Event {
  id: string;
  kind: string;
  // inline comment redacted marker
  payload: unknown;
}

export type Shape = {
  w: number; // inline comment redacted marker
  h: number;
};

export const CONFIG = {
  retries: 3, // inline comment redacted marker
  verbose: false,
};
