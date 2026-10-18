export const A = 1; // SECRET_A original comment
const MID = 5;
const B = 2; // SECRET_B original comment

export interface Event {
  id: string;
  // SECRET_C original comment
  name: string;
  /** SECRET_D original docstring */
  payload: unknown;
}
