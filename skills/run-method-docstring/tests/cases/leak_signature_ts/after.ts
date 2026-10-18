/** SECRET_IFACE interface docstring */
export interface Event {
  id: string;
  kind: string;
  /** SECRET_FIELD field docstring */
  payload: unknown;
}

/** SECRET_TYPE type docstring */
export type Shape = {
  w: number; // SECRET_W trailing
  h: number;
};

/** SECRET_CONST const docstring */
export const CONFIG = {
  retries: 3, // SECRET_R trailing
  verbose: false,
};
