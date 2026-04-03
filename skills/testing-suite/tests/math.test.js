const { add, subtract, multiply, divide } = require('./math');

describe('Math Module', () => {
  describe('add', () => {
    test('should add two numbers correctly', () => {
      expect(add(2, 3)).toBe(5);
    });

    test('should handle negative numbers', () => {
      expect(add(-2, 3)).toBe(1);
    });
  });

  describe('subtract', () => {
    test('should subtract two numbers correctly', () => {
      expect(subtract(5, 3)).toBe(2);
    });
  });

  describe('multiply', () => {
    test('should multiply two numbers correctly', () => {
      expect(multiply(4, 3)).toBe(12);
    });
  });

  describe('divide', () => {
    test('should divide two numbers correctly', () => {
      expect(divide(10, 2)).toBe(5);
    });

    test('should throw error when dividing by zero', () => {
      expect(() => divide(10, 0)).toThrow('Division by zero');
    });
  });
});
