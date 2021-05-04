
var paused_value_visualizer = 0;

let sketch = function(val)
{
  val.yoff = 0.0;
  val.max_height = window.innerHeight;
  val.max_width = window.innerWidth;

  val.current_color = 0;
  val.next_color = 0;
  val.current_color_two = 0;
  val.next_color_two = 0;
  val.current_color_three = 0;
  val.next_color_three = 0;

  val.color_index = 0;
  val.paused = 1;
  val.amt = 0;

  val.setup = function(){
    var canvas = val.createCanvas(val.max_width, val.max_height);
    canvas.position(0,0,'relative');
    val.current_color = val.select_new_color();
    val.next_color = val.select_new_color();
    val.current_color_two = val.select_new_color();
    val.next_color_two = val.select_new_color();
    val.current_color_three = val.select_new_color();
    val.next_color_three = val.select_new_color();
    val.amt = 0.01;
  }

  val.draw = function(){
    val.draw_lines(0);
  }

  val.draw_lines = function(increase){
    val.clear();
    val.noStroke();
    if (val.amt >= 1)
    {
      val.next_color = val.select_new_color();
      val.next_color_two = val.select_new_color();
      val.next_color_three = val.select_new_color();
      val.amt = 0.01;
    }

    val.current_color = val.lerpColor(val.current_color, val.next_color, val.amt);
    val.current_color_two = val.lerpColor(val.current_color_two, val.next_color_two, val.amt);
    val.current_color_three = val.lerpColor(val.current_color_three, val.next_color_three, val.amt);


    var original_plane = [];
    let xoff = 0;
    for (let x = 0; x <= val.width; x += 10) {
      var y = 0;
      var first;
      var second;
      first = paused_value_visualizer == 1 ? 0 : val.max_height/2+10;
      second = paused_value_visualizer == 1 ? val.max_height : val.max_height/2-10;
      original_plane.push(val.map(val.noise(xoff, val.yoff), 0, 1, first, second));
      xoff += 0.05;
    }

    val.fill(val.current_color);
    val.beginShape();
    var w = 0;
    for (let x = 0; x < original_plane.length; x++)
    {
      val.vertex(w, original_plane[x]);
      w+=10;
    }
    val.vertex(val.width, val.height);
    val.vertex(0, val.height);
    val.endShape(val.CLOSE);

    val.fill(val.current_color_two);
    val.beginShape();
    w = 0;
    for (let x = 0; x < original_plane.length; x++)
    {
      val.vertex(w, original_plane[x]+30);
      w+=10;
    }
    val.vertex(val.width, val.height);
    val.vertex(0, val.height);
    val.endShape(val.CLOSE);

    val.fill(val.current_color_three);
    val.beginShape();
    w = 0;
    for (let x = 0; x < original_plane.length; x++)
    {
      val.vertex(w, original_plane[x]+60);
      w+=10;
    }
    val.vertex(val.width, val.height);
    val.vertex(0, val.height);
    val.endShape(val.CLOSE);

    val.amt += 0.005;
    val.yoff += 0.01;
  }

  val.play_pause = function()
  {
    val.paused = 1 - val.paused;
  }

  val.select_new_color = function()
  {
    var i = Math.floor(Math.random() * 10);
    //val.current_color = next_color;
    switch(i)
      {
        case 0:
          next_color = val.color(255,255,0);
          break;
        case 1:
          next_color = val.color(255,165,0);
          break;
        case 2:
          next_color = val.color(255,69,0);
          break;
        case 3:
          next_color = val.color(255,140,0);
          break;
        case 4:
          next_color = val.color(255,215,0);
          break;
        case 5:
          next_color = val.color(63, 0, 255);
          break;
        case 6:
          next_color = val.color(255,0,255);
          break;
        case 7:
          next_color = val.color(0,255,255);
          break;
        case 8:
          next_color = val.color(63, 0, 255);
          break;
        case 9:
          next_color = val.color(138,43,226);
          break;
      }
      return next_color;
  }
};