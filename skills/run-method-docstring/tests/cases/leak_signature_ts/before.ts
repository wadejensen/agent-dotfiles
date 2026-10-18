export interface Event {
  id: string;
  kind: string;
  payload: unknown;
}

export type Shape = {
  w: number;
  h: number;
};

export const CONFIG = {
  retries: 3,
  verbose: false,
};
