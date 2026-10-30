export const ANA_ID = '1';
export const DANIEL_ID = '2';

export interface Person {
  id: string;
  name: string;
  emoji: string;
  color: string;
}

export const PEOPLE: Record<string, Person> = {
  [DANIEL_ID]: { id: DANIEL_ID, name: 'Daniel', emoji: 'D', color: '#2563eb' },
  [ANA_ID]: { id: ANA_ID, name: 'Ana', emoji: 'A', color: '#ec4899' },
};

export const PERSON_LIST: Person[] = [PEOPLE[DANIEL_ID], PEOPLE[ANA_ID]];
