// Utility functions for general use in the app

// Converts milliseconds to a MM:SS format
function millisToMinutesAndSeconds(milliseconds) {
  let minutes = Math.floor(milliseconds / 60000);
  let seconds = ((milliseconds % 60000) / 1000).toFixed(0);

  return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
}