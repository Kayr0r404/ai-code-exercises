function validateRequiredFields(userData, fields) {
  const errors = [];
  for (const field of fields) {
    if (!userData[field] || userData[field].trim() === '') {
      errors.push(`${field} is required for registration`);
    }
  }
  return errors;
}

function validateUsername(username, checkExisting) {
  const errors = [];
  if (!username) return errors;
  if (username.length < 3) {
    errors.push('Username must be at least 3 characters long');
  } else if (username.length > 20) {
    errors.push('Username must be at most 20 characters long');
  } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    errors.push('Username can only contain letters, numbers, and underscores');
  } else if (checkExisting && checkExisting.usernameExists(username)) {
    errors.push('Username is already taken');
  }
  return errors;
}

function validatePassword(password, confirmPassword) {
  const errors = [];
  if (!password) return errors;
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  } else if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  } else if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  } else if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one number');
  } else if (!/[^A-Za-z0-9]/.test(password)) {
    errors.push('Password must contain at least one special character');
  }
  if (confirmPassword !== undefined && confirmPassword !== password) {
    errors.push('Password and confirmation do not match');
  }
  return errors;
}

function validateEmail(email, isRegistration, checkExisting) {
  const errors = [];
  if (email === undefined) return errors;
  if (email.trim() === '') {
    if (isRegistration) {
      errors.push('Email is required');
    }
  } else {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      errors.push('Email format is invalid');
    } else if (checkExisting && checkExisting.emailExists(email)) {
      errors.push('Email is already registered');
    }
  }
  return errors;
}

function validateDateOfBirth(dateOfBirth) {
  const errors = [];
  if (dateOfBirth === undefined || dateOfBirth === '') return errors;
  const dobDate = new Date(dateOfBirth);
  if (isNaN(dobDate.getTime())) {
    errors.push('Date of birth is not a valid date');
  } else {
    const now = new Date();
    const minAgeDate = new Date(now.getFullYear() - 13, now.getMonth(), now.getDate());
    const maxAgeDate = new Date(now.getFullYear() - 120, now.getMonth(), now.getDate());
    if (dobDate > now) {
      errors.push('Date of birth cannot be in the future');
    } else if (dobDate > minAgeDate) {
      errors.push('You must be at least 13 years old');
    } else if (dobDate < maxAgeDate) {
      errors.push('Invalid date of birth (age > 120 years)');
    }
  }
  return errors;
}

function validateAddress(address) {
  const errors = [];
  if (address === undefined || address === '') return errors;
  if (typeof address === 'object') {
    const requiredAddressFields = ['street', 'city', 'zip', 'country'];
    for (const field of requiredAddressFields) {
      if (!address[field] || address[field].trim() === '') {
        errors.push(`Address ${field} is required`);
      }
    }
    if (address.zip && address.country) {
      if (address.country === 'US' && !/^\d{5}(-\d{4})?$/.test(address.zip)) {
        errors.push('Invalid US ZIP code format');
      } else if (address.country === 'CA' && !/^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$/.test(address.zip)) {
        errors.push('Invalid Canadian postal code format');
      } else if (address.country === 'UK' && !/^[A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}$/.test(address.zip)) {
        errors.push('Invalid UK postal code format');
      }
    }
  } else {
    errors.push('Address must be an object with required fields');
  }
  return errors;
}

function validatePhone(phone) {
  const errors = [];
  if (phone === undefined || phone === '') return errors;
  if (!/^\+?[\d\s\-()]{10,15}$/.test(phone)) {
    errors.push('Phone number format is invalid');
  }
  return errors;
}

function validateCustomFields(userData, customValidations) {
  const errors = [];
  if (!customValidations) return errors;
  for (const validation of customValidations) {
    const field = validation.field;
    if (userData[field] !== undefined) {
      const valid = validation.validator(userData[field], userData);
      if (!valid) {
        errors.push(validation.message || `Invalid value for ${field}`);
      }
    }
  }
  return errors;
}

function validateUserData(userData, options = {}) {
  const errors = [];
  const isRegistration = options.isRegistration || false;

  if (isRegistration) {
    const requiredForRegistration = ['username', 'email', 'password', 'confirmPassword'];
    errors.push(...validateRequiredFields(userData, requiredForRegistration));
    errors.push(...validateUsername(userData.username, options.checkExisting));
    errors.push(...validatePassword(userData.password, userData.confirmPassword));
  } else {
    const requiredForProfile = ['firstName', 'lastName', 'dateOfBirth', 'address'];
    for (const field of requiredForProfile) {
      if (userData[field] !== undefined && userData[field] === '') {
        errors.push(`${field} cannot be empty if provided`);
      }
    }
  }

  errors.push(...validateEmail(userData.email, isRegistration, options.checkExisting));
  errors.push(...validateDateOfBirth(userData.dateOfBirth));
  errors.push(...validateAddress(userData.address));
  errors.push(...validatePhone(userData.phone));
  errors.push(...validateCustomFields(userData, options.customValidations));

  return errors;
}

module.exports = { validateUserData };