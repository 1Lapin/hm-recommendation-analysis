import { motion } from "framer-motion";

// Each individual digit column — stacked 0-9, spring-animated from 0 to target
function DigitColumn({ digit, height = 80, delay = 0 }) {
  return (
    <span className="relative inline-flex overflow-hidden" style={{ width: "0.56em", height }}>
      <motion.span
        className="absolute inset-0 flex flex-col"
        initial={{ translateY: 0 }}
        animate={{ translateY: -digit * height }}
        transition={{
          type: "spring",
          stiffness: 35,
          damping: 16,
          mass: 0.8,
          delay: 0.4 + delay / 1000,
        }}
      >
        {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => (
          <span
            key={n}
            className="flex items-center justify-center font-bold text-blue-400"
            style={{ height, fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}
          >
            {n}
          </span>
        ))}
      </motion.span>
    </span>
  );
}

export default function AnimatedCounter({ value, height = 72 }) {
  const chars = String(value).split("");

  return (
    <span className="inline-flex items-baseline">
      {chars.map((ch, i) => {
        if (ch === ",") {
          return (
            <span
              key={i}
              className="inline-flex items-end pb-2 font-bold text-blue-400"
              style={{ height, width: "0.28em", fontFamily: "'JetBrains Mono', 'Courier New', monospace" }}
            >
              ,
            </span>
          );
        }
        let precedingDigits = 0;
        for (let j = 0; j < i; j++) {
          if (chars[j] !== ",") precedingDigits++;
        }
        return (
          <DigitColumn
            key={i}
            digit={Number(ch)}
            height={height}
            delay={precedingDigits * 80}
          />
        );
      })}
    </span>
  );
}
