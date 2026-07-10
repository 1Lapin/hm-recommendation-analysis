import { motion } from "framer-motion";

// Simple CSS-based hero badge — no Three.js required.
// Shows profile photo on a floating card-like badge.
export default function ProfileBadge({ photo = "/avatar.jpg", name = "黄晓媛", role = "数据分析师" }) {
  return (
    <div className="relative mx-auto w-fit">
      {/* Shadow glow ring */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.7, delay: 0.2 }}
        className="absolute -inset-2 rounded-full bg-blue-400/20 blur-2xl"
      />

      {/* Outer ring */}
      <motion.div
        initial={{ opacity: 0, rotate: -10 }}
        animate={{ opacity: 1, rotate: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="relative rounded-full border-2 border-white/[0.08] bg-gradient-to-br from-white/[0.04] to-transparent p-2 backdrop-blur-sm"
      >
        {/* Photo */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="h-44 w-44 overflow-hidden rounded-full"
        >
          <img
            src={photo}
            alt={name}
            className="h-full w-full object-cover"
          />
        </motion.div>
      </motion.div>
    </div>
  );
}
