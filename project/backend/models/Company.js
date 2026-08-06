const mongoose = require('mongoose');

const CompanySchema = new mongoose.Schema(
  {
    websiteName: {
      type: String,
      required: true,
      trim: true
    },
    url: {
      type: String,
      required: true,
      trim: true
    },
    enrichedProfile: {
      type: mongoose.Schema.Types.Mixed,
      required: true
    }
  },
  {
    timestamps: true // adds createdAt and updatedAt automatically
  }
);

module.exports = mongoose.model('Company', CompanySchema);
