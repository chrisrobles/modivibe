// Utility functions for general use in the app
// Converts milliseconds to a MM:SS format
function millisToMinutesAndSeconds(millis) {
  let minutes = Math.floor(millis / 60000);
  let seconds = ((millis % 60000) / 1000).toFixed(0);

  return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
}